import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from .models import RegistroRetiro
from .forms import RegistroRetiroForm
from Modulo_admin.models import Alumno, Inspector, Curso
from .utils import enviar_notificacion_retiro
import time
from django.views.decorators.csrf import csrf_exempt

def verificar_apoderado(request):
    """Vista AJAX para verificar si un RUT corresponde a un apoderado autorizado"""
    if request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        rut_apoderado = request.GET.get('rut_apoderado')
        
        # Buscar alumnos donde este RUT sea apoderado titular, suplente o familiar autorizado
        alumnos_apoderado = []
        nombre_apoderado = None  # Inicializar variable para el nombre del apoderado
        
        try:
            # Intentar diferentes campos posibles para el RUT del apoderado
            posibles_campos_apoderado = [
                ('apoderado_titular', 'rut_apoderadoT'),
                ('apoderado_suplente', 'rut_apoderadoS'),
                ('familiar_1', 'rut_familiar_1'),
                ('familiar_2', 'rut_familiar_2')
            ]
            
            for nombre_campo, rut_campo in posibles_campos_apoderado:
                try:
                    # Crear un diccionario de filtro dinámicamente
                    filtro = {rut_campo: rut_apoderado}
                    alumnos = Alumno.objects.filter(**filtro)
                    
                    for alumno in alumnos:
                        # Determinar el tipo de persona basado en el campo
                        tipo_persona = "Otro"
                        
                        # Asignar el nombre del apoderado según el campo que coincidió
                        if nombre_campo == 'apoderado_titular':
                            tipo_persona = "Apoderado"
                            if not nombre_apoderado:
                                nombre_apoderado = alumno.apoderado_titular
                        elif nombre_campo == 'apoderado_suplente':
                            tipo_persona = "Apoderado Suplente"
                            if not nombre_apoderado:
                                nombre_apoderado = alumno.apoderado_suplente
                        elif nombre_campo == 'familiar_1':
                            tipo_persona = "Familiar"
                            if not nombre_apoderado:
                                nombre_apoderado = alumno.familiar_1
                        elif nombre_campo == 'familiar_2':
                            tipo_persona = "Familiar"
                            if not nombre_apoderado:
                                nombre_apoderado = alumno.familiar_2
                        
                        alumnos_apoderado.append({
                            'rut': alumno.rut,
                            'nombre': alumno.nombre,
                            'curso': str(alumno.curso),
                            'tipo_persona': tipo_persona
                        })
                except Exception as e:
                    print(f"Error al procesar campo {nombre_campo}: {str(e)}")
                    # Si el campo no existe en el modelo, simplemente continuamos
                    continue
            
            if alumnos_apoderado:
                # Si no se encontró el nombre, usar un valor por defecto
                if not nombre_apoderado:
                    nombre_apoderado = "Apoderado Autorizado"
                
                print(f"Nombre del apoderado encontrado: {nombre_apoderado}")
                
                return JsonResponse({
                    'valido': True,
                    'alumnos': alumnos_apoderado,
                    'nombre_apoderado': nombre_apoderado,  # Devolver el nombre del apoderado
                    'mensaje': 'Persona autorizada verificada correctamente'
                })
            else:
                return JsonResponse({
                    'valido': False,
                    'mensaje': 'El RUT ingresado no corresponde a ninguna persona autorizada para retirar estudiantes'
                })
        except Exception as e:
            print(f"Error en verificar_apoderado: {str(e)}")
            return JsonResponse({
                'error': f'Error al procesar la solicitud: {str(e)}',
                'valido': False
            })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)



def obtener_datos_alumno(request):
    """Vista AJAX para obtener los datos de un alumno por su RUT"""
    if request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        rut_estudiante = request.GET.get('rut_estudiante')
        rut_apoderado = request.GET.get('rut_apoderado')
        
        try:
            # Buscar el alumno por RUT
            alumno = Alumno.objects.get(rut=rut_estudiante)
            
            # Verificar si el apoderado está autorizado para este alumno
            # Intentar diferentes campos posibles
            autorizado = False
            tipo_persona = None
            
            # Verificar apoderado titular
            for campo in ['apoderado_titular', 'rut_apoderadoT', 'rut_apoderado_titular']:
                try:
                    if getattr(alumno, campo) == rut_apoderado:
                        autorizado = True
                        tipo_persona = "Apoderado"
                        break
                except:
                    continue
            
            # Verificar apoderado suplente
            if not autorizado:
                for campo in ['apoderado_suplente', 'rut_apoderadoS', 'rut_apoderado_suplente']:
                    try:
                        if getattr(alumno, campo) == rut_apoderado:
                            autorizado = True
                            tipo_persona = "Apoderado Suplente"
                            break
                    except:
                        continue
            
            # Verificar familiar 1
            if not autorizado:
                for campo in ['familiar_1', 'rut_familiar_1']:
                    try:
                        if getattr(alumno, campo) == rut_apoderado:
                            autorizado = True
                            tipo_persona = "Otro"
                            break
                    except:
                        continue
            
            # Verificar familiar 2
            if not autorizado:
                for campo in ['familiar_2', 'rut_familiar_2']:
                    try:
                        if getattr(alumno, campo) == rut_apoderado:
                            autorizado = True
                            tipo_persona = "Otro"
                            break
                    except:
                        continue
            
            # Buscar el inspector a cargo del curso
            inspector = None
            try:
                inspectores = Inspector.objects.filter(cursos=alumno.curso)
                if inspectores.exists():
                    inspector = inspectores.first().nombre
            except Exception:
                inspector = "No asignado"
            
            # Devolver los datos del alumno
            return JsonResponse({
                'encontrado': True,
                'autorizado': autorizado,
                'tipo_persona': tipo_persona,
                'nombre': alumno.nombre,
                'curso': str(alumno.curso),
                'inspector': inspector or "No asignado",
                'mensaje': 'Datos del alumno obtenidos correctamente'
            })
        
        except Alumno.DoesNotExist:
            return JsonResponse({
                'encontrado': False,
                'mensaje': 'No se encontró ningún alumno con ese RUT'
            })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtener_datos_alumno(request):
    """Vista AJAX para obtener los datos de un alumno por su RUT"""
    if request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        rut_estudiante = request.GET.get('rut_estudiante')
        rut_apoderado = request.GET.get('rut_apoderado')
        
        try:
            # Buscar el alumno por RUT
            alumno = Alumno.objects.get(rut=rut_estudiante)
            
            # Verificar si el apoderado está autorizado para este alumno
            es_apoderado_titular = alumno.apoderado_titular == rut_apoderado
            es_apoderado_suplente = alumno.apoderado_suplente == rut_apoderado
            es_familiar_1 = alumno.rut_familiar_1 == rut_apoderado
            es_familiar_2 = alumno.rut_familiar_2 == rut_apoderado
            
            autorizado = es_apoderado_titular or es_apoderado_suplente or es_familiar_1 or es_familiar_2
            
            # Determinar el tipo de relación
            tipo_persona = None
            if es_apoderado_titular:
                tipo_persona = "Apoderado"
            elif es_apoderado_suplente:
                tipo_persona = "Apoderado Suplente"
            elif es_familiar_1 or es_familiar_2:
                tipo_persona = "Otro"
            
            # Buscar el inspector a cargo del curso
            inspector = None
            try:
                inspectores = Inspector.objects.filter(cursos=alumno.curso)
                if inspectores.exists():
                    inspector = inspectores.first().nombre
            except Exception:
                inspector = "No asignado"
            
            # Devolver los datos del alumno
            return JsonResponse({
                'encontrado': True,
                'autorizado': autorizado,
                'tipo_persona': tipo_persona,
                'nombre': alumno.nombre,
                'curso': str(alumno.curso),
                'inspector': inspector or "No asignado",
                'mensaje': 'Datos del alumno obtenidos correctamente'
            })
        
        except Alumno.DoesNotExist:
            return JsonResponse({
                'encontrado': False,
                'mensaje': 'No se encontró ningún alumno con ese RUT'
            })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)



def obtener_telefono_inspector(inspector_nombre):
    """
    Obtiene el número de teléfono del inspector basado en su nombre
    """
    try:
        # Aquí deberías implementar la lógica para obtener el teléfono del inspector
        inspector = Inspector.objects.get(nombre=inspector_nombre)
        return inspector.telefono

    except Exception as e:
        print(f"Error al obtener teléfono del inspector: {str(e)}")
        return None


def retiro_justificacion_view(request):
    return render(request, 'retiro_justificacion.html')

def formulario_retiro_view(request):
    if request.method == "POST":
        form = RegistroRetiroForm(request.POST)
        try:
            if form.is_valid():
                # Guardamos el formulario
                registro = form.save(commit=False)
                registro.hora_retiro = timezone.now()
                registro.save()
                
                # NUEVO: Obtener el número de teléfono del inspector a cargo
                inspector_telefono = obtener_telefono_inspector(registro.inspector_cargo)
                
                # NUEVO: Enviar notificación por WhatsApp si hay teléfono disponible
                if inspector_telefono:
                    success, message = enviar_notificacion_retiro(
                        inspector_telefono,
                        registro.nombre_estudiante,
                        str(registro.curso),
                        registro.nombre_persona_retira,
                        registro.get_motivo_retiro_display()
                    )
                    
                    if not success:
                        # Registrar el error pero continuar con el proceso
                        print(f"Error al enviar notificación WhatsApp: {message}")
                        # Opcionalmente guardar este error en un log o en la base de datos
                
                # Redirigir a una página de confirmación
                return redirect('Modulo_alumnos:confirmacion_retiro', registro_id=registro.id)
            else:
                print("Errores en el formulario:", form.errors)
        except Exception as e:
            print("Error al procesar el formulario:", str(e))
            # Puedes mostrar un mensaje de error al usuario
            messages.error(request, f"Error al procesar el formulario: {str(e)}")
    else:
        form = RegistroRetiroForm()
    
    return render(request, 'formulario_retiro.html', {'form': form})



def confirmacion_retiro_view(request, registro_id):
    try:
        registro = RegistroRetiro.objects.get(id=registro_id)
        print(f"Mostrando confirmación para retiro {registro_id}")
        return render(request, 'confirmacion_retiro.html', {'registro': registro})
    except RegistroRetiro.DoesNotExist:
        print(f"No se encontró el retiro {registro_id} para la confirmación")
        messages.error(request, "No se encontró el registro de retiro solicitado.")
        return redirect('Modulo_alumnos:retiro_justificacion')

def formulario_justificacion_view(request):
    return render(request, 'formulario_justificar.html')


@csrf_exempt
def procesar_retiro(request):
    """
    Vista para procesar un retiro de alumno y enviar notificación al inspector.
    """
    print("\n--- INICIO procesar_retiro ---")
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Obtener datos del formulario
            rut_persona_retira = request.POST.get('rut_persona_retira')
            nombre_persona_retira = request.POST.get('nombre_persona_retira')
            rut_estudiante = request.POST.get('rut_estudiante')
            nombre_estudiante = request.POST.get('nombre_estudiante')
            curso = request.POST.get('curso')
            motivo_retiro = request.POST.get('motivo_retiro')
            inspector_cargo = request.POST.get('inspector_cargo')
            
            print(f"Datos recibidos: rut_persona_retira={rut_persona_retira}, nombre_persona_retira={nombre_persona_retira}, "
                  f"rut_estudiante={rut_estudiante}, nombre_estudiante={nombre_estudiante}, curso={curso}, "
                  f"motivo_retiro={motivo_retiro}, inspector_cargo={inspector_cargo}")
            
            # Validar datos
            if not all([rut_persona_retira, nombre_persona_retira, rut_estudiante, nombre_estudiante, curso, motivo_retiro, inspector_cargo]):
                error_msg = "Todos los campos son obligatorios"
                print(f"Error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)
            
            # Crear registro de retiro
            registro = RegistroRetiro.objects.create(
                rut_persona_retira=rut_persona_retira,
                nombre_persona_retira=nombre_persona_retira,
                rut_estudiante=rut_estudiante,
                nombre_estudiante=nombre_estudiante,
                curso=curso,
                motivo_retiro=motivo_retiro,
                inspector_cargo=inspector_cargo,
                estado='waiting'  # Estado inicial: en espera
            )
            
            print(f"Registro creado con ID: {registro.id}")
            
            # Obtener el número de teléfono del inspector
            inspector_telefono = obtener_telefono_inspector(inspector_cargo)
            
            if not inspector_telefono:
                error_msg = f"No se encontró el número de teléfono para el inspector: {inspector_cargo}"
                print(f"Error: {error_msg}")
                registro.estado = 'timeout'
                registro.mensaje_respuesta = error_msg
                registro.save()
                return JsonResponse({'error': error_msg, 'retiro_id': registro.id}, status=400)
            
            print(f"Teléfono del inspector: {inspector_telefono}")
            
            # Enviar notificación al inspector
            success, message = enviar_notificacion_retiro(
                inspector_telefono=inspector_telefono,
                alumno_nombre=nombre_estudiante,
                curso=curso,
                apoderado_nombre=nombre_persona_retira,
                motivo=dict(RegistroRetiro.MOTIVO_CHOICES).get(motivo_retiro, motivo_retiro),
                retiro_id=registro.id
            )
            
            if not success:
                error_msg = f"Error al enviar notificación: {message}"
                print(f"Error: {error_msg}")
                registro.estado = 'timeout'
                registro.mensaje_respuesta = error_msg
                registro.save()
                return JsonResponse({'error': error_msg, 'retiro_id': registro.id}, status=500)
            
            print(f"Notificación enviada correctamente")
            
            response_data = {
                'success': True,
                'message': 'Retiro registrado y notificación enviada al inspector',
                'retiro_id': registro.id
            }
            print(f"Respuesta: {response_data}")
            print("--- FIN procesar_retiro ---\n")
            return JsonResponse(response_data)
            
        except Exception as e:
            error_msg = f"Error al procesar el retiro: {str(e)}"
            print(f"Error: {error_msg}")
            print("--- FIN procesar_retiro ---\n")
            return JsonResponse({'error': error_msg}, status=500)
    
    print(f"Método no permitido: {request.method}")
    print("--- FIN procesar_retiro ---\n")
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Nueva vista para verificar el estado del retiro
def verificar_estado_retiro(request):
    if request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        retiro_id = request.GET.get('retiro_id')
        print(f"Verificando estado del retiro {retiro_id}")
        
        try:
            registro = RegistroRetiro.objects.get(id=retiro_id)
            
            # Verificar si ha pasado demasiado tiempo (timeout después de 2 minutos)
            tiempo_espera = timezone.now() - registro.hora_retiro
            if tiempo_espera.total_seconds() > 120 and registro.estado == 'waiting':
                registro.estado = 'timeout'
                registro.save()
                
                redirect_url = reverse('Modulo_alumnos:confirmacion_retiro', args=[registro.id])
                print(f"Timeout para retiro {retiro_id}, redirigiendo a: {redirect_url}")
                
                return JsonResponse({
                    'status': 'timeout',
                    'message': 'Tiempo de espera agotado',
                    'redirect_url': redirect_url
                })
            
            # Devolver el estado actual
            redirect_url = reverse('Modulo_alumnos:confirmacion_retiro', args=[registro.id])
            print(f"Estado actual del retiro {retiro_id}: {registro.estado}, redirigiendo a: {redirect_url}")
            
            return JsonResponse({
                'status': registro.estado,
                'message': registro.mensaje_respuesta or '',
                'redirect_url': redirect_url
            })
            
        except RegistroRetiro.DoesNotExist:
            print(f"No se encontró el retiro {retiro_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'Registro de retiro no encontrado'
            })
        except Exception as e:
            print(f"Error al verificar estado del retiro {retiro_id}: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error al verificar estado: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


@csrf_exempt
def actualizar_estado_retiro(request):
    """
    Vista para actualizar el estado de un retiro desde el bot de WhatsApp.
    Esta vista está exenta de verificación CSRF porque el bot no puede obtener el token.
    """
    if request.method == 'POST':
        try:
            # Imprimir el cuerpo de la solicitud para depuración
            body = request.body.decode('utf-8')
            print(f"Cuerpo de la solicitud: {body}")
            
            # Parsear los datos JSON del cuerpo de la solicitud
            data = json.loads(body)
            print(f"Datos recibidos: {data}")
            
            retiro_id = data.get('retiro_id')
            status = data.get('status')
            message = data.get('message')
            
            print(f"retiro_id: {retiro_id}, status: {status}, message: {message}")
            
            if not retiro_id or not status:
                error_msg = 'Se requieren los campos retiro_id y status'
                print(f"Error: {error_msg}")
                return JsonResponse({
                    'success': False,
                    'message': error_msg
                }, status=400)
            
            # Buscar el registro de retiro
            try:
                registro = RegistroRetiro.objects.get(id=retiro_id)
                print(f"Registro encontrado: {registro}")
            except RegistroRetiro.DoesNotExist:
                error_msg = f'No se encontró el retiro con ID {retiro_id}'
                print(f"Error: {error_msg}")
                return JsonResponse({
                    'success': False,
                    'message': error_msg
                }, status=404)
            
            # Actualizar el estado
            registro.estado = status
            registro.mensaje_respuesta = message
            registro.save()
            print(f"Registro actualizado: estado={status}, mensaje={message}")
            
            return JsonResponse({
                'success': True,
                'message': 'Estado actualizado correctamente'
            })
            
        except json.JSONDecodeError as e:
            error_msg = f'Formato JSON inválido: {str(e)}'
            print(f"Error: {error_msg}")
            return JsonResponse({
                'success': False,
                'message': error_msg
            }, status=400)
        except Exception as e:
            error_msg = f'Error al procesar la solicitud: {str(e)}'
            print(f"Error: {error_msg}")
            return JsonResponse({
                'success': False,
                'message': error_msg
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    }, status=405)



