from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import RegistroRetiro
from .forms import RegistroRetiroForm
from Modulo_admin.models import Alumno, Inspector, Curso

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

# Las demás vistas permanecen igual
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
    registro = RegistroRetiro.objects.get(id=registro_id)
    return render(request, 'confirmacion_retiro.html', {'registro': registro})

def formulario_justificacion_view(request):
    return render(request, 'formulario_justificar.html')
