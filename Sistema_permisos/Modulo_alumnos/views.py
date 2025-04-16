from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import RegistroRetiro
from .forms import RegistroRetiroForm
from Modulo_admin.models import Alumno, Inspector, Curso

def retiro_justificacion_view(request):
    return render(request, 'retiro_justificacion.html')

def verificar_apoderado(request):
    """Vista AJAX para verificar si un RUT corresponde a un apoderado autorizado"""
    if request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        rut_apoderado = request.GET.get('rut_apoderado')
        
        # Buscar alumnos donde este RUT sea apoderado titular o suplente
        alumnos_apoderado = Alumno.objects.filter(
            apoderado_titular=rut_apoderado
        ) | Alumno.objects.filter(
            apoderado_suplente=rut_apoderado
        )
        
        if alumnos_apoderado.exists():
            # Si es apoderado, devolver los alumnos asociados
            alumnos_data = []
            for alumno in alumnos_apoderado:
                alumnos_data.append({
                    'rut': alumno.rut,
                    'nombre': alumno.nombre,
                    'curso': alumno.curso
                })
            
            return JsonResponse({
                'valido': True,
                'alumnos': alumnos_data,
                'mensaje': 'Apoderado verificado correctamente'
            })
        else:
            # Si no es apoderado, devolver error
            return JsonResponse({
                'valido': False,
                'mensaje': 'El RUT ingresado no corresponde a ningún apoderado registrado'
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
            es_apoderado = (alumno.apoderado_titular == rut_apoderado or 
                           alumno.apoderado_suplente == rut_apoderado)
            
            # Si es familiar registrado, también está autorizado
            es_familiar = (alumno.familiar_1 and alumno.familiar_1_telefono and 
                          (alumno.familiar_1 == rut_apoderado)) or \
                         (alumno.familiar_2 and alumno.familiar_2_telefono and 
                          (alumno.familiar_2 == rut_apoderado))
            
            # Determinar el tipo de relación
            tipo_persona = None
            if alumno.apoderado_titular == rut_apoderado:
                tipo_persona = 'Apoderado'
            elif alumno.apoderado_suplente == rut_apoderado:
                tipo_persona = 'Apoderado Suplente'
            elif es_familiar:
                tipo_persona = 'Otro'
            
            # Buscar el inspector a cargo del curso
            inspector = None
            try:
                curso_obj = Curso.objects.get(nombre=alumno.curso)
                inspectores = Inspector.objects.filter(cursos=curso_obj)
                if inspectores.exists():
                    inspector = inspectores.first().nombre
            except (Curso.DoesNotExist, Exception):
                inspector = "No asignado"
            
            # Devolver los datos del alumno
            return JsonResponse({
                'encontrado': True,
                'autorizado': es_apoderado or es_familiar,
                'tipo_persona': tipo_persona,
                'nombre': alumno.nombre,
                'curso': alumno.curso,
                'inspector': inspector or "No asignado",
                'mensaje': 'Datos del alumno obtenidos correctamente'
            })
        
        except Alumno.DoesNotExist:
            return JsonResponse({
                'encontrado': False,
                'mensaje': 'No se encontró ningún alumno con ese RUT'
            })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def formulario_retiro_view(request):
    if request.method == "POST":
        form = RegistroRetiroForm(request.POST)
        if form.is_valid():
            # Guardamos el formulario
            registro = form.save(commit=False)
            registro.hora_retiro = timezone.now()
            registro.save()
            
            # Redirigir a una página de confirmación
            return redirect('Modulo_alumnos:confirmacion_retiro', registro_id=registro.id)
    else:
        form = RegistroRetiroForm()
    
    return render(request, 'formulario_retiro.html', {'form': form})

def confirmacion_retiro_view(request, registro_id):
    registro = RegistroRetiro.objects.get(id=registro_id)
    return render(request, 'confirmacion_retiro.html', {'registro': registro})

def formulario_justificacion_view(request):
    return render(request, 'formulario_justificar.html')
