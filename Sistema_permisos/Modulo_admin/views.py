from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import AdministradorForm, AreasForm
from .models import Administrador, Areas
from Modulo_funcionarios.models import RegistroSalida
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse


# Create your views here.
def loginadmin_view(request):
    return render(request, "login.html")


def login_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}')
            return redirect('Modulo_admin:grafico')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'login.html')



def logout_admin(request):
    if request.method == 'POST':
        logout(request)
        return redirect('Modulo_admin:login_admin')
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('Modulo_admin:login_admin')


    


# Vista grafico - Versión corregida
@login_required(login_url='Modulo_admin:login_admin')
def graficoview(request):
    # Obtener las áreas desde la base de datos
    areas = Areas.objects.all()
    
    nombre_areas = []
    cantidad_permisos = []
    
    for area in areas:
        # Contar permisos por área usando el campo area_perteneciente
        count = RegistroSalida.objects.filter(area_perteneciente=area.nombre).count()
        nombre_areas.append(area.nombre)
        cantidad_permisos.append(count)
    
    # Convertir a JSON
    import json
    nombre_areas_json = json.dumps(nombre_areas)
    cantidad_permisos_json = json.dumps(cantidad_permisos)
    
    context = {
        'nombre_areas': nombre_areas_json,
        'cantidad_permisos': cantidad_permisos_json
    }
    
    return render(request, "grafico.html", context)


# Vista tabla_general
@login_required(login_url='Modulo_admin:login_admin')
def tabla_generalview(request):
    # Iniciar con todos los permisos completados
    permisos = RegistroSalida.objects.filter(hora_regreso__isnull=False)
    
    # Obtener parámetros de filtrado
    busqueda = request.GET.get('busqueda', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    # Aplicar búsqueda por nombre o RUT si se proporciona
    if busqueda:
        # Limpiar el RUT para la búsqueda (quitar puntos y guiones)
        busqueda_rut = busqueda.replace('.', '').replace('-', '')
        permisos = permisos.filter(
            Q(nombre__icontains=busqueda) | 
            Q(rut__icontains=busqueda) |
            Q(rut__icontains=busqueda_rut)
        )
    
    # Aplicar filtro de rango de fechas personalizado
    if fecha_inicio:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            permisos = permisos.filter(hora_salida__date__gte=fecha_inicio_obj)
        except ValueError:
            pass
            
    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            # Ajustar fecha_fin para incluir todo el día
            fecha_fin_obj = datetime.combine(fecha_fin_obj, datetime.max.time())
            permisos = permisos.filter(hora_salida__date__lte=fecha_fin_obj)
        except ValueError:
            pass
    
    # Ordenar por fecha de salida (más reciente primero)
    permisos = permisos.order_by('-hora_salida')
    
    # Pasar todos los parámetros al contexto
    context = {
        'permisos': permisos,
        'busqueda': busqueda,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_registros': permisos.count()
    }
    
    return render(request, "tabla_general.html", context)

# Vista tabla_salidas
@login_required(login_url='Modulo_admin:login_admin')
def tabla_salidasview(request):
    # Obtener todas las salidas activas (sin hora de regreso)
    salidas = RegistroSalida.objects.filter(hora_regreso__isnull=True)
    
    # Obtener parámetros de filtrado
    busqueda = request.GET.get('busqueda', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    # Aplicar búsqueda por nombre o RUT si se proporciona
    if busqueda:
        # Limpiar el RUT para la búsqueda (quitar puntos y guiones)
        busqueda_rut = busqueda.replace('.', '').replace('-', '')
        salidas = salidas.filter(
            Q(nombre__icontains=busqueda) | 
            Q(rut__icontains=busqueda) |
            Q(rut__icontains=busqueda_rut)
        )
    
    # Aplicar filtro de rango de fechas personalizado
    if fecha_inicio:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            salidas = salidas.filter(hora_salida__date__gte=fecha_inicio_obj)
        except ValueError:
            pass
            
    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            # Ajustar fecha_fin para incluir todo el día
            fecha_fin_obj = datetime.combine(fecha_fin_obj, datetime.max.time())
            salidas = salidas.filter(hora_salida__date__lte=fecha_fin_obj)
        except ValueError:
            pass
    
    # Calcular el tiempo transcurrido para cada salida
    ahora = timezone.now()
    for salida in salidas:
        salida.tiempo_transcurrido = ahora - salida.hora_salida
    
    # Ordenar por hora de salida (más reciente primero)
    salidas = sorted(salidas, key=lambda x: x.hora_salida, reverse=True)
    
    # Pasar todos los parámetros al contexto
    context = {
        'salidas': salidas,
        'busqueda': busqueda,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_registros': len(salidas)
    }
    
    return render(request, "tabla_salidas.html", context)



# Vista tabla_administradores
@login_required(login_url='Modulo_admin:login_admin')
def administradores_view(request):
    administradores = Administrador.objects.all()
    return render(request, 'administradores.html', {'administradores': administradores})


#Agregar administrador
@login_required(login_url='Modulo_admin:login_admin')
def registrar_administrador_view(request):
    if request.method == 'POST':
        form = AdministradorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Administrador registrado correctamente')
            return redirect('Modulo_admin:administradores')
    else:
        form = AdministradorForm()
    return render(request, 'administrador.html', {'form': form})            


@login_required(login_url='Modulo_admin:login_admin')
def editar_administrador_view(request, id):
    administrador = get_object_or_404(Administrador, id=id)
    if request.method == 'POST':
        form = AdministradorForm(request.POST, instance=administrador)
        if form.is_valid():
            form.save()
            messages.success(request, 'Administrador editado')
            return redirect('Modulo_admin:administradores')
    else:
        form = AdministradorForm(instance=administrador)
    return render(request, 'administrador.html', {'form': form})


#Eliminar administrador
@login_required(login_url='Modulo_admin:login_admin')
def eliminar_administrador_view(request, id):
    administrador = get_object_or_404(Administrador, id=id)
    administrador.delete()
    messages.success(request, 'Administrador eliminado correctamente')
    return redirect('Modulo_admin:administradores')


#Vista tabla_areas
@login_required(login_url='Modulo_admin:login_admin')
def areas_view(request):
    areas = Areas.objects.all()
    return render(request, 'areas.html', {'areas': areas})

#Agregar areas
@login_required(login_url='Modulo_admin:login_admin')
def registrar_areas_view(request):
    if request.method == 'POST':
        form = AreasForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área registrada correctamente')
            return redirect('Modulo_admin:area')
        else:
            form = AreasForm()
    return render(request, 'areas.html', {'form': form})


#Editar areas
@login_required(login_url='Modulo_admin:login_admin')
def editar_areas_view(request, id):
    areas = get_object_or_404(Areas, id=id)
    if request.method == 'POST':
        form = AreasForm(request.POST, instance=areas)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área editada')
            return redirect('Modulo_admin:area')
    else:
        form = AreasForm(instance=areas)
    return render(request, 'editar_areas.html', {'form': form})


#Eliminar areas
@login_required(login_url='Modulo_admin:login_admin')
def eliminar_areas_view(request, id):
    area = get_object_or_404(Areas, id=id)
    area.delete()
    messages.success(request, 'Área eliminado correctamente')
    return redirect('Modulo_admin:area')


#Vista tabla_areas
@login_required(login_url='Modulo_admin:login_admin')
def tabla_areasview(request):
    return render(request, "areas.html")

def exportar_permisos_pdf(request):
    """Exporta la tabla de permisos como HTML con descarga automática"""
    try:
        # Obtener los permisos completados (con hora de regreso)
        permisos = RegistroSalida.objects.filter(hora_regreso__isnull=False)
        
        # Preparar contexto para la plantilla
        context = {
            'permisos': permisos,
            'fecha_generacion': timezone.now(),
            'titulo': 'Registro de Permisos Completados',
            'total_registros': permisos.count(),
            'auto_print': True  # Indica a la plantilla que debe imprimir automáticamente
        }
        
        # Renderizar la plantilla a una cadena HTML
        html_string = render_to_string('reportes_permisos_completados.html', context, request=request)
        
        # Crear respuesta HTTP con el HTML
        response = HttpResponse(html_string, content_type='text/html')
        
        # Configurar encabezados para forzar descarga
        filename = f"permisos_{timezone.now().strftime('%Y%m%d_%H%M%S')}.html"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        import traceback
        print(f"Error al generar reporte de permisos: {str(e)}")
        print(traceback.format_exc())
        messages.error(request, f"Error al generar el reporte: {str(e)}")
        return redirect('Modulo_admin:historial_permisos')

def exportar_salidas_pdf(request):
    """Exporta la tabla de salidas activas como HTML con descarga automática"""
    try:
        # Obtener las salidas activas (sin hora de regreso)
        salidas = RegistroSalida.objects.filter(hora_regreso__isnull=True)
        
        # Preparar contexto para la plantilla
        context = {
            'salidas': salidas,
            'fecha_generacion': timezone.now(),
            'titulo': 'Registro de Salidas Activas',
            'total_registros': salidas.count(),
            'auto_print': True  # Indica a la plantilla que debe imprimir automáticamente
        }
        
        # Renderizar la plantilla a una cadena HTML
        html_string = render_to_string('reportes_salidas.html', context, request=request)
        
        # Crear respuesta HTTP con el HTML
        response = HttpResponse(html_string, content_type='text/html')
        
        # Configurar encabezados para forzar descarga
        filename = f"salidas_{timezone.now().strftime('%Y%m%d_%H%M%S')}.html"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        import traceback
        print(f"Error al generar reporte de salidas: {str(e)}")
        print(traceback.format_exc())
        messages.error(request, f"Error al generar el reporte: {str(e)}")
        return redirect('Modulo_admin:historial_salidas')