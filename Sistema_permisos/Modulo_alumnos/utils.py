import requests
import json

def enviar_notificacion_retiro(inspector_telefono, alumno_nombre, curso, apoderado_nombre, motivo, retiro_id):
    """
    Envía una notificación de retiro al inspector a través de WhatsApp
    """
    print(f"\n--- INICIO enviar_notificacion_retiro para retiro_id: {retiro_id} ---")
    # URL del servidor del bot de WhatsApp
    bot_url = "http://localhost:3000/send-message"
    
    # Formatear el mensaje
    mensaje = f"""🔔 *NOTIFICACIÓN DE RETIRO* 🔔

*ID:* {retiro_id}
*Alumno:* {alumno_nombre}
*Curso:* {curso}
*Retirado por:* {apoderado_nombre}
*Motivo:* {motivo}

Responda con:
1️⃣ - Confirmar retiro
2️⃣ - Alumno ocupado en actividad (Prueba, reunion, etc.)
3️⃣ - Alumno no se encuentra en el establecimiento
*Porfavor, solo indicar el numero de opcion*

"""
    
    # Datos para la solicitud
    data = {
        "phone": inspector_telefono,
        "message": mensaje,
        "retiro_id": str(retiro_id)  # Convertir a string para asegurar compatibilidad
    }
    
    print(f"Enviando notificación al bot con datos: {data}")
    
    try:
        # Enviar solicitud al bot
        response = requests.post(bot_url, json=data)
        print(f"Respuesta del bot: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            # Intentar parsear la respuesta JSON
            try:
                resp_data = response.json()
                print(f"Respuesta JSON del bot: {resp_data}")
                
                # Verificar si el bot asoció correctamente el retiro_id
                if resp_data.get('retiro_id') == str(retiro_id):
                    print(f"Bot confirmó asociación del retiro_id: {retiro_id}")
                else:
                    print(f"Advertencia: El bot no confirmó la asociación del retiro_id")
            except:
                print("No se pudo parsear la respuesta del bot como JSON")
                
            print("--- FIN enviar_notificacion_retiro ---\n")
            return True, "Notificación enviada correctamente"
        else:
            error_msg = f"Error al enviar notificación: {response.text}"
            print(f"Error: {error_msg}")
            print("--- FIN enviar_notificacion_retiro ---\n")
            return False, error_msg
    
    except Exception as e:
        error_msg = f"Error de conexión: {str(e)}"
        print(f"Error: {error_msg}")
        print("--- FIN enviar_notificacion_retiro ---\n")
        return False, error_msg
