from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import AdministradorForm, AdministradorEditForm , AreasForm, CambiarPasswordForm
from .models import Administrador, Areas
from Modulo_funcionarios.models import RegistroSalida
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from functools import wraps
from django.db import transaction


# Decorador para verificar si el usuario es staff
def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para realizar esta acción')
            return redirect('Modulo_admin:administradores')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Create your views here.
def loginadmin_view(request):
    return render(request, "login.html")


def login_admin(request):
    if request.method == 'POST':
        rut = request.POST.get('rut', '')
        password = request.POST.get('password', '')

        # Autenticar usando el RUT como nombre de usuario
        user = authenticate(request, username=rut, password=password)

        if user is not None:
            # Verificar si el usuario está asociado a un administrador
            try:
                administrador = Administrador.objects.get(user=user)
                login(request, user)
                messages.success(request, f'Bienvenido, {administrador.nombre}')
                return redirect('Modulo_admin:grafico')
            except Administrador.DoesNotExist:
                messages.error(request, 'Este usuario no tiene permisos de administrador')
        else:
            messages.error(request, 'RUT o contraseña incorrectos')
    return render(request, 'login.html')



def logout_admin(request):
    if request.method == 'POST':
        logout(request)
        return redirect('Modulo_admin:login_admin')
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('Modulo_admin:login_admin')


    


# Vista grafico 
@login_required(login_url='Modulo_admin:login_admin')
def graficoview(request):
    # Obtener las áreas desde la base de datos
    areas = Areas.objects.all()
    
    nombre_areas = []
    cantidad_permisos = []
    meses = ["Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    meses_num = {
        "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6, "Julio": 7, 
        "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
    }

    # Inicializar los datos por mes para cada área
    datos_por_mes={}


    

    # Llenar los datos por mes con la cantidad de permisos
    for area in areas:
        nombre_areas.append(area.nombre)

        count = RegistroSalida.objects.filter(area_perteneciente = area.nombre).count()
        cantidad_permisos.append(count)

        datos_por_mes[area.nombre]= {}

        #Llenar los datos por mes
        for mes_nombre in meses:
            mes_num = meses_num[mes_nombre]
            cantidad = RegistroSalida.objects.filter(area_perteneciente = area.nombre, hora_salida__month=mes_num).count()
            datos_por_mes[area.nombre][mes_nombre] = cantidad
    # Convertir a JSON
    import json
    nombre_areas_json = json.dumps(nombre_areas)
    cantidad_permisos_json = json.dumps(cantidad_permisos)
    datos_por_mes_json = json.dumps(datos_por_mes)
    meses_json = json.dumps(meses)


    context = {
        'nombre_areas': nombre_areas_json,
        'cantidad_permisos': cantidad_permisos_json,
        'datos_por_mes': datos_por_mes_json,
        'meses': meses_json
    }
    
    return render(request, "funcionarios_folder/grafico_folder/grafico.html", context)


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
    
    return render(request, "funcionarios_folder/tablas_folder/tabla_general.html", context)




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
    limite_24_horas = timedelta(hours=24)
    
    for salida in salidas:
        tiempo_transcurrido = ahora - salida.hora_salida
        
        # Si han pasado más de 24 horas, mostrar "Regreso no registrado"
        if tiempo_transcurrido > limite_24_horas:
            salida.tiempo_transcurrido = "Regreso no registrado"
        else:
            salida.tiempo_transcurrido = tiempo_transcurrido
    
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
    
    return render(request, "funcionarios_folder/tablas_folder/tabla_salidas.html", context)






# Vista tabla_administradores
@login_required(login_url='Modulo_admin:login_admin')
def administradores_view(request):
    administradores = Administrador.objects.all()
    return render(request, 'funcionarios_folder/administradores_folder/administradores.html', {'administradores': administradores})


#Agregar administrador
@login_required(login_url='Modulo_admin:login_admin')
@staff_required
def registrar_administrador_view(request):
    if request.method == 'POST':
        form = AdministradorForm(request.POST)
        if form.is_valid():
            # Obtener datos del formulario
            rut = form.cleaned_data['rut']
            nombre = form.cleaned_data['nombre']
            area = form.cleaned_data['area']
            password = form.cleaned_data['password1']
            is_superuser = request.POST.get('is_superuser') == 'on'
            
            # Crear el usuario de Django
            try:
                user = User.objects.create_user(
                    username=rut,  # Se usa el RUT como nombre de usuario
                    password=password,
                    first_name=nombre
                )
                
                # Establecer permisos de superusuario si se marcó el checkbox
                user.is_staff = True  # Todos los administradores son staff
                user.is_superuser = is_superuser
                user.save()
                
                # Guardar el administrador sin commit para asignar el usuario
                administrador = form.save(commit=False)
                administrador.user = user
                administrador.save()
                
                messages.success(request, 'Administrador registrado correctamente')
                return redirect('Modulo_admin:administradores')
            except Exception as e:
                # Si hay un error, eliminamos el usuario si se creó
                if 'user' in locals():
                    user.delete()
                messages.error(request, f'Error al registrar administrador: {str(e)}')
        else:
            # Si el formulario no es válido, mostrar errores
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    else:
        form = AdministradorForm()
    
    return render(request, 'funcionarios_folder/administradores_folder/administrador.html', {'form': form})


@login_required(login_url='Modulo_admin:login_admin')
@staff_required
def editar_administrador_view(request, id):
    administrador = get_object_or_404(Administrador, id=id)
    
    if request.method == 'POST':
        form = AdministradorEditForm(request.POST, instance=administrador)
        if form.is_valid():
            # Actualizar el administrador
            admin = form.save(commit=False)
            
            # Verificar si se marcó el checkbox de superusuario
            is_superuser = request.POST.get('is_superuser') == 'on'
        
            if admin.user:
                # Actualizar usuario existente
                admin.user.first_name = form.cleaned_data['nombre']
                admin.user.is_superuser = is_superuser
                admin.user.save()
            else:
                # Crear nuevo usuario con contraseña temporal
                user = User.objects.create_user(
                    username=admin.rut,
                    password='temporal123',  # Contraseña temporal
                    first_name=form.cleaned_data['nombre']
                )
                user.is_staff = True
                user.is_superuser = is_superuser
                user.save()
                admin.user = user
            
            admin.save()
            messages.success(request, 'Administrador editado correctamente')
            return redirect('Modulo_admin:administradores')
    else:
        form = AdministradorEditForm(instance=administrador)
    
    return render(request, 'funcionarios_folder/administradores_folder/administrador.html', {'form': form, 'is_edit': True})


@login_required(login_url='Modulo_admin:login_admin')
@staff_required
def cambiar_password_view(request, id):
    administrador = get_object_or_404(Administrador, id=id)
    
    if not administrador.user:
        messages.error(request, 'Este administrador no tiene un usuario asociado')
        return redirect('Modulo_admin:administradores')
    
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            # Cambiar la contraseña
            administrador.user.set_password(form.cleaned_data['password1'])
            administrador.user.save()
            messages.success(request, 'Contraseña actualizada correctamente')
            return redirect('Modulo_admin:administradores')
    else:
        form = CambiarPasswordForm()
    
    return render(request, 'funcionarios_folder/administradores_folder/administrador.html', {'form': form, 'administrador': administrador})




#Eliminar administrador
@login_required(login_url='Modulo_admin:login_admin')
@staff_required
def eliminar_administrador_view(request, id):
    administrador = get_object_or_404(Administrador, id=id)
    
    # Si tiene un usuario asociado, eliminarlo también
    if administrador.user:
        administrador.user.delete()
    
    administrador.delete()
    messages.success(request, 'Administrador eliminado correctamente')
    return redirect('Modulo_admin:administradores')


#Vista tabla_areas
@login_required(login_url='Modulo_admin:login_admin')
def areas_view(request):
    # objects ya filtra las áreas eliminadas gracias al manager personalizado
    areas = Areas.objects.all()
    return render(request, 'funcionarios_folder/areas_folder/areas.html', {'areas': areas})

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
    return render(request, 'funcionarios_folder/areas_folder/areas.html', {'form': form})


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
    return render(request, 'funcionarios_folder/areas_folder/editar_areas.html', {'form': form})


#Eliminar areas
@login_required(login_url='Modulo_admin:login_admin')
def eliminar_areas_view(request, id):
   # Usar all_objects para encontrar incluso áreas eliminadas
    area = get_object_or_404(Areas.all_objects, id=id)
    
    # Marcar como eliminada en lugar de eliminar físicamente
    area.is_deleted = True
    area.deleted_at = timezone.now()
    area.save()
    
    messages.success(request, 'Área eliminada correctamente')
    return redirect('Modulo_admin:area')

#Vista tabla_areas
@login_required(login_url='Modulo_admin:login_admin')
def tabla_areasview(request):
    return render(request, "funcionarios_folder/areas_folder/areas.html")

def exportar_permisos_pdf(request):
    """Exporta la tabla de permisos como HTML con descarga automática"""
    return redirect('Modulo_admin:historial_permisos')





def exportar_salidas_pdf(request):
    """Exporta la tabla de salidas activas como HTML con descarga automática"""
    return redirect('Modulo_admin:historial_salidas')