const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const fetch = require('node-fetch');

// Configuración del servidor Express
const app = express();
app.use(express.json());
const PORT = process.env.PORT || 3000;

// Configuración del cliente de WhatsApp
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});


app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
    if (req.method === 'POST' && req.body) {
        console.log('Cuerpo de la solicitud:', JSON.stringify(req.body));
    }
    next();
});

// Variable para rastrear si el cliente está listo
let clientReady = false;

// Mapa para rastrear retiros activos: número de teléfono -> retiroId
const activeRetiros = {};

// Evento cuando se necesita escanear el código QR
client.on('qr', (qr) => {
    console.log('QR RECIBIDO, escanea con WhatsApp:');
    qrcode.generate(qr, { small: true });
});

// Evento cuando el cliente está listo
client.on('ready', () => {
    clientReady = true;
    console.log('Cliente WhatsApp listo!');
});

// Evento para mensajes entrantes
client.on('message', async (message) => {
    console.log(`Mensaje recibido: ${message.body} de ${message.from}`);
    
    // Extraer el número de teléfono sin @c.us
    const phoneNumber = message.from.split('@')[0];
    console.log(`Número de teléfono extraído: ${phoneNumber}`);
    console.log(`Mapa de retiros activos:`, activeRetiros);

    const validResponses = ['1', '2', '3'];
    const cleanResponse = message.body.trim().toLowerCase();
    
    // Procesar respuestas numéricas (1, 2, 3)
    if (validResponses.includes(cleanResponse)) {
        console.log(`Respuesta válida detectada: ${cleanResponse}`);
        
        // Verificar si tenemos un retiroId asociado a este número
        if (activeRetiros[phoneNumber]) {
            console.log(`RetiroId encontrado para ${phoneNumber}: ${activeRetiros[phoneNumber]}`);
            const responseMessage = await processResponse(message.from, cleanResponse);
            await client.sendMessage(message.from, responseMessage);
            console.log(`Respuesta enviada al inspector: "${responseMessage}"`);
        } else {
            console.log(`No se encontró retiroId para ${phoneNumber}, buscando en mensajes anteriores...`);
            // Intentar extraer el ID del retiro de mensajes anteriores
            try {
                const chat = await message.getChat();
                await chat.fetchMessages({limit: 20}); // Aumentar el límite para buscar más mensajes
                
                let retiroId = null;
                
                // Buscar el ID del retiro en los mensajes anteriores
                for (let i = chat.messages.length - 1; i >= 0; i--) {
                    const msg = chat.messages[i];
                    if (msg.fromMe && msg.body.includes('*ID:*')) {
                        console.log(`Mensaje con ID encontrado: "${msg.body}"`);
                        const idMatch = msg.body.match(/\*ID:\*\s*(\d+)/);
                        if (idMatch && idMatch[1]) {
                            retiroId = idMatch[1];
                            // Guardar el retiroId para futuras referencias
                            activeRetiros[phoneNumber] = retiroId;
                            console.log(`RetiroId encontrado en mensajes: ${retiroId}`);
                            break;
                        }
                    }
                }
                
                if (retiroId) {
                    const responseMessage = await processResponse(message.from, cleanResponse);
                    await client.sendMessage(message.from, responseMessage);
                    console.log(`Respuesta enviada al inspector: "${responseMessage}"`);
                } else {
                    console.log(`No se encontró retiroId en los mensajes para ${phoneNumber}`);
                    await client.sendMessage(message.from, 'No se pudo identificar a qué retiro corresponde esta respuesta. Por favor, contacte al administrador.');
                }
            } catch (error) {
                console.error('Error al procesar mensaje:', error);
                await client.sendMessage(message.from, 'Ocurrió un error al procesar tu respuesta. Por favor, contacte al administrador.');
            }
        }
    } else {
        console.log(`Mensaje no reconocido como respuesta válida: "${message.body}"`);
    }
});

// Iniciar el cliente de WhatsApp
client.initialize();

// Función para procesar respuestas
async function processResponse(from, response) {
    // Determinar qué respuesta se dio
    let status, message;

    const phoneNumber = from.split('@')[0];
    
    // Obtener el retiroId asociado con este número
    const retiroId = activeRetiros[phoneNumber];

    if (!retiroId) {
        console.error('No se encontró retiroId para el número:', phoneNumber);
        return 'No se pudo identificar a qué retiro corresponde esta respuesta. Por favor, contacte al administrador.';
    }
    if (response === '1' || response === '2') {
        status = 'confirmed';
        message = response === '1' ? 'Retiro confirmado por el inspector' : 'El alumno se encuentra ocupado en una actividad';
    } else if (response === '3') {
        status = 'rejected';
        message = 'El inspector a indicado que el alumno no se encuentra en el establecimiento. Por favor dirijase con la inspectora de salida. ';
    } else {
        return 'Respuesta no reconocida. Por favor, responde con 1, 2 o 3.';
    }
    
    console.log(`Enviando actualización para retiroId: ${retiroId}, status: ${status}, message: ${message}`);

    // Actualizar el estado en Django
    try {
        const updateResponse = await fetch('http://localhost:8000/Modulo_alumnos/actualizar-estado-retiro/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                retiro_id: retiroId,
                status: status,
                message: message
            }),
        });
        
        const responseText = await updateResponse.text();
        console.log('Respuesta del servidor:', responseText);
        
        try {
            const responseData = JSON.parse(responseText);
            
            if (updateResponse.ok) {
                console.log('Estado actualizado correctamente:', responseData);
                const responses = {
                    '1': 'Has confirmado el retiro del alumno. Gracias!',
                    '2': 'Has indicado que el alumno se encuentra ocupado en una actividad. Gracias!',
                    '3': 'Has indicado que el alumno ya no se encuentra en el establecimiento. Gracias por tu respuesta.'
                };
                return responses[response];
            } else {
                console.error('Error al actualizar estado:', responseData);
                return 'Se recibió tu respuesta, pero hubo un problema al actualizar el sistema. Un administrador revisará el caso.';
            }
        } catch (e) {
            console.error('Error al parsear la respuesta:', e);
            return 'Se recibió tu respuesta, pero hubo un problema al procesar la respuesta del servidor.';
        }
    } catch (error) {
        console.error('Error al actualizar estado:', error);
        return 'Se recibió tu respuesta, pero hubo un problema de conexión. Un administrador revisará el caso.';
    }
}

// Endpoint para enviar mensajes
app.post('/send-message', async (req, res) => {
    if (!clientReady) {
        return res.status(503).json({ success: false, message: 'El cliente de WhatsApp no está listo' });
    }
    
    const { phone, message, retiro_id } = req.body;
    console.log("Datos recibidos en /send-message:", { phone, message, retiro_id });
    
    if (!phone || !message) {
        return res.status(400).json({ success: false, message: 'Se requiere número de teléfono y mensaje' });
    }
    
    try {
        // Formatear número de teléfono
        const formattedPhone = formatPhoneNumber(phone);
        console.log('Número formateado:', formattedPhone);
        
        // Extraer solo el número sin @c.us
        const phoneNumber = formattedPhone.split('@')[0];
        
        // Si se proporciona un retiro_id, lo guardamos en el mapa
        if (retiro_id) {
            activeRetiros[phoneNumber] = retiro_id;
            console.log(`Asociando número ${phoneNumber} con retiroId ${retiro_id}`);
            console.log('Mapa actualizado:', activeRetiros);
        }
        
        // Enviar mensaje
        await client.sendMessage(formattedPhone, message);
        
        res.json({ 
            success: true, 
            message: 'Mensaje enviado correctamente',
            phoneNumber,
            retiro_id: activeRetiros[phoneNumber]
        });
    } catch (error) {
        console.error('Error al enviar mensaje:', error);
        res.status(500).json({ success: false, message: 'Error al enviar mensaje', error: error.message });
    }
});

// Función para formatear número de teléfono
function formatPhoneNumber(phone) {
    // Eliminar espacios, guiones y paréntesis
    let cleaned = phone.replace(/\s+/g, '').replace(/-/g, '').replace(/[()]/g, '');
    
    // Asegurarse que tenga el código de país (Chile: 56)
    if (!cleaned.startsWith('+')) {
        if (!cleaned.startsWith('56')) {
            cleaned = '56' + cleaned;
        }
        cleaned = '+' + cleaned;
    }

    cleaned = '+' + cleaned.substring(1).replace(/\D/g, '');
    
    // Formato para WhatsApp: [código país]@c.us
    return `${cleaned.substring(1)}@c.us`;
}

// Endpoint para verificar el estado del bot
app.get('/status', (req, res) => {
    res.json({
        status: clientReady ? 'ready' : 'initializing',
        activeRetiros: Object.keys(activeRetiros).length,
        retiros: activeRetiros
    });
});

// Endpoint para depuración - listar retiros activos
app.get('/active-retiros', (req, res) => {
    res.json({
        activeRetiros
    });
});

// Iniciar servidor Express
app.listen(PORT, () => {
    console.log(`Servidor escuchando en el puerto ${PORT}`);
});

