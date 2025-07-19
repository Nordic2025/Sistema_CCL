from django.shortcuts import render, redirect
from .models import RegistroSalida
from .forms import Modulo_funcionariosForm  
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from Modulo_admin.models import Areas



def get_area_encargado(request):
    if request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        encargado_id = request.GET.get('encargado_id')
        try:
            area = Areas.objects.get(id=encargado_id)
            return JsonResponse({'area': area.nombre})
        except Areas.DoesNotExist:
            return JsonResponse({'error': 'Área no encontrada'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def registrar_salida(request):
    if request.method == "POST":
        form = Modulo_funcionariosForm(request.POST)
        if form.is_valid():
            # Se registra el formulario sin guardar aun y se genera automáticamente el código
            registro = form.save(commit=False) 
            
            area_encargado = Areas.objects.get(id=request.POST.get('autorizado_por')).nombre
            registro.area_perteneciente = area_encargado
            
            registro.hora_salida = timezone.now() 
            registro.save()  
            
            return redirect('Modulo_funcionarios:confirmacion_permiso', registro_id=registro.id)
    else:
        form = Modulo_funcionariosForm()

    return render(request, 'formulario_permisos.html', {'form': form})


def confirmar_regreso(request, codigo):
    registro = get_object_or_404(RegistroSalida, codigo_registro=codigo, hora_regreso__isnull=True)
    registro.hora_regreso = timezone.now()
    registro.save()
    return render(request, 'confirmar_registro.html', {'registro': registro})

def ingreso_salida(request):

    return render(request, 'ingreso_salida.html')

def formulario_permisos(request):

    return render(request, 'formulario_permisos.html')

def formulario_regreso(request):
    if request.method == "POST":
        codigo = request.POST.get('codigo_registro')
        try:
            registro = RegistroSalida.objects.get(codigo_registro=codigo, hora_regreso__isnull=True)
            return redirect('Modulo_funcionarios:confirmar_regreso', codigo=codigo)
        except RegistroSalida.DoesNotExist:
            return render(request, 'formulario_regreso.html', {'error': 'Código no válido o ya utilizado'})
    
    return render(request, 'formulario_regreso.html')

def confirmacion_permiso(request, registro_id=None):
    if registro_id:
        registro = get_object_or_404(RegistroSalida, id=registro_id)
    else:
        registro = RegistroSalida.objects.latest('hora_salida')
    
    return render(request, 'confirmacion_permiso.html', {'registro': registro})


def recuperar_codigo(request):
    if request.method == "POST":
        rut = request.POST.get('rut')
        try:
            # Buscar el permiso más reciente sin hora de regreso para ese RUT
            ultimo_permiso = RegistroSalida.objects.filter(
                rut=rut,
                hora_regreso__isnull=True
            ).order_by('-hora_salida').first()
            
            if ultimo_permiso:
                # Si hay permisos activos para ese RUT, se devuelve el código del último permiso
                return render(request, 'recuperar_codigo.html', {
                    'codigo': ultimo_permiso.codigo_registro
                })
            else:
                # Si no hay permisos activos para ese RUT
                return render(request, 'recuperar_codigo.html', {
                    'error': 'No se encontraron permisos activos para este RUT'
                })
        except Exception as e:
            return render(request, 'recuperar_codigo.html', {
                'error': f'Error al buscar: {str(e)}'
            })
    
    return render(request, 'recuperar_codigo.html')

# Vista para manejar solicitudes AJAX
def recuperar_codigo_ajax(request):
    if request.method == "POST":
        rut = request.POST.get('rut')
        try:
            # Buscar el permiso más reciente sin hora de regreso para ese RUT
            ultimo_permiso = RegistroSalida.objects.filter(
                rut=rut,
                hora_regreso__isnull=True
            ).order_by('-hora_salida').first()
            
            if ultimo_permiso:
                return JsonResponse({
                    'codigo': ultimo_permiso.codigo_registro
                })
            else:
                return JsonResponse({
                    'error': 'No se encontraron permisos activos para este RUT'
                })
        except Exception as e:
            return JsonResponse({
                'error': f'Error al buscar: {str(e)}'
            })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


