from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from .forms import AdministradorForm, AdministradorEditForm , AreasForm, CambiarPasswordForm, CursoForm, AlumnoForm, FamiliarForm, InspectorForm
from .models import Administrador, Areas, Curso, Alumno, Inspector, AlumnoEgresado
from Modulo_funcionarios.models import RegistroSalida
from Modulo_alumnos.models import RegistroRetiro
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from functools import wraps
from django.db import transaction
import re
from django.core.paginator import Paginator


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
                return redirect('Modulo_admin:inicio')
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


#Vista de Inicio en el modulo admin
@login_required(login_url='Modulo_admin:login_admin')
def inicio_view(request):

    dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    

    # Obtener la fecha actual y la fecha de hace 7 dias
    fecha_actual = timezone.now().date()
    fecha_inicio = fecha_actual - timedelta(days=6)

    # Inicializacion de las listas
    fechas = []
    datos_permisos = []
    datos_retiros = []

    # Generar datos para cada dia
    for i in range(7):
        dia = fecha_inicio + timedelta(days=i)
        dia_siguiente = dia + timedelta(days=1)

        # Formato para mostrar los dias
        dia_semana = dia.weekday()
        nombre_dia = dias_semana[dia_semana]
        fechas.append(nombre_dia)

        # Conteo de permisos completados de ese dia
        permisos_dia = RegistroSalida.objects.filter(
            hora_salida__date__gte=dia, 
            hora_salida__date__lt=dia_siguiente, 
            hora_regreso__isnull=False
        ).count()
        datos_permisos.append(permisos_dia)

        # RegistroRetiro
        retiros_dia = RegistroRetiro.objects.filter(hora_retiro__gte= dia, hora_retiro__lt= dia_siguiente).count()
        datos_retiros.append(retiros_dia)

    # Obtener estadistica de los permisos
    permisos_activos = RegistroSalida.objects.filter(hora_regreso__isnull=True).count()

    # Obtener los ultimos 5 permisos
    permisos_recientes = RegistroSalida.objects.order_by('-hora_salida')[:5]

    #Obtener estadistica de los retiros
    retiros_hoy = RegistroRetiro.objects.filter(hora_retiro__gte = dia).count()

    #Obtener todos los alumnos
    total_alumnos = Alumno.objects.all().count()

    # Convertir listas a formato JSON para el template
    import json
    fechas_json = json.dumps(fechas)
    datos_permisos_json = json.dumps(datos_permisos)
    datos_retiros_json = json.dumps(datos_retiros)

    # Contexto
    context = {
        'fechas': fechas_json,
        'datos_permisos': datos_permisos_json,
        'datos_retiros': datos_retiros_json,
        'permisos_activos': permisos_activos,
        'permisos_recientes': permisos_recientes,
        'retiros_hoy': retiros_hoy,
        'total_alumnos': total_alumnos,
    }

    return render(request, 'inicio.html', context)



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
    
    queryset = RegistroSalida.objects.filter(hora_regreso__isnull=False).order_by('-hora_salida')

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
    

    paginator = Paginator(permisos, 35)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    print("Permisos en la página actual:", len(page_obj))
    print("Número de página:", page_obj.number)
    print("Total de páginas:", page_obj.paginator.num_pages)
    
    # Pasar todos los parámetros al contexto
    context = {
        'permisos': page_obj,
        'busqueda': busqueda,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_registros': permisos.count(),
        'page_obj': page_obj
    }
    
    return render(request, "funcionarios_folder/tablas_folder/tabla_general.html", context)




# Vista tabla_salidas
@login_required(login_url='Modulo_admin:login_admin')
def tabla_salidasview(request):
    # Obtener todas las salidas activas (sin hora de regreso)
    salidas = RegistroSalida.objects.filter(hora_regreso__isnull=True)
    
    queryset = RegistroSalida.objects.filter(hora_regreso__isnull=True).order_by('-hora_salida')

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
    
    paginator = Paginator(salidas, 35)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Pasar todos los parámetros al contexto
    context = {
        'salidas': page_obj,
        'busqueda': busqueda,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total_registros': len(salidas),
        'page_obj': page_obj
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

#MODULO ALUMNO / CURSOS

@login_required(login_url='Modulo_admin:login_admin')
def cursos_view(request):
    # objects ya filtra los cursos eliminados gracias al manager personalizado
    cursos = Curso.objects.all()
    return render(request, 'alumnos_folder/cursos_folder/cursos.html', {'cursos': cursos})

@login_required(login_url='Modulo_admin:login_admin')
def registrar_curso_view(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Curso registrado correctamente')
            return redirect('Modulo_admin:cursos')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    return redirect('Modulo_admin:cursos')

@login_required(login_url='Modulo_admin:login_admin')
def editar_curso_view(request, id):
    curso = get_object_or_404(Curso, id=id)
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Curso editado correctamente')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    return redirect('Modulo_admin:cursos')

@login_required(login_url='Modulo_admin:login_admin')
def eliminar_curso_view(request, id):
    # Usar all_objects para encontrar incluso cursos eliminados
    curso = get_object_or_404(Curso.all_objects, id=id)
    
    # Marcar como eliminado en lugar de eliminar físicamente
    curso.is_deleted = True
    curso.deleted_at = timezone.now()
    curso.save()
    
    messages.success(request, 'Curso eliminado correctamente')
    return redirect('Modulo_admin:cursos')


#MODULO ALUMNOS / INPECTORES.

@login_required(login_url='Modulo_admin:login_admin')
def inspectores_view(request):
    # objects ya filtra los inspectores eliminados gracias al manager personalizado
    inspectores = Inspector.objects.all().prefetch_related('cursos')
    cursos = Curso.objects.all()

    inspector_salida_exists = Inspector.objects.filter(is_salida=True).exists()
    return render(request, 'alumnos_folder/inspectores_folder/inspectores.html', {
        'inspectores': inspectores,
        'cursos': cursos,
        'inspector_salida_exists': inspector_salida_exists
    })

@login_required(login_url='Modulo_admin:login_admin')
def registrar_inspector_view(request):
    if request.method == 'POST':
        form = InspectorForm(request.POST)
        if form.is_valid():
            is_salida = request.POST.get('is_salida') == 'on'
            if is_salida and Inspector.objects.filter(is_salida=True).exists():
                messages.error(request, 'Ya existe un Inspector General en el sistema')
                return redirect('Modulo_admin:inspectores')
            
            # Primero, guarda el inspector sin asignar cursos
            inspector = form.save(commit=False)
            inspector.is_salida = is_salida
            
            # Agregar campos de estado activo
            inspector.is_active = request.POST.get('is_active') == 'on'
            
            # Guardar el inspector para obtener un ID
            inspector.save()
            
            # Ahora que el inspector tiene un ID, podemos asignar cursos
            if is_salida:
                # Si el inspector es el de salida, asignarle todos los cursos
                todos_cursos = Curso.objects.all()
                inspector.cursos.set(todos_cursos)
            else:
                cursos_ids = request.POST.getlist('cursos')
                inspector.cursos.set(cursos_ids)
                
            messages.success(request, 'Inspector registrado correctamente')
            return redirect('Modulo_admin:inspectores')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    return redirect('Modulo_admin:inspectores')




@login_required(login_url='Modulo_admin:login_admin')
def editar_inspector_view(request, id):
    inspector = get_object_or_404(Inspector, id=id)
    if request.method == 'POST':
        form = InspectorForm(request.POST, instance=inspector)
        if form.is_valid():
            is_salida = request.POST.get('is_salida') == 'on'
            if is_salida and not inspector.is_salida and Inspector.objects.filter(is_salida=True).exists():
                messages.error(request, 'Ya existe un Inspector de Salida en el sistema')
                return redirect('Modulo_admin:inspectores')
            
            # Actualizar campos
            inspector = form.save(commit=False)
            inspector.is_salida = is_salida
            inspector.is_active = request.POST.get('is_active') == 'on'
            inspector.save()

            if is_salida:
                todos_cursos = Curso.objects.all()
                inspector.cursos.set(todos_cursos)
            else:
                cursos_ids = request.POST.getlist('cursos')
                inspector.cursos.set(cursos_ids)
                
            messages.success(request, 'Inspector editado correctamente')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    return redirect('Modulo_admin:inspectores')


@login_required(login_url='Modulo_admin:login_admin')
def cambiar_estado_inspector_view(request, id):
    inspector = get_object_or_404(Inspector, id=id)
    
    # Cambiar el estado del inspector
    inspector.is_active = not inspector.is_active
    inspector.save()
    
    estado = "activado" if inspector.is_active else "desactivado"
    messages.success(request, f'Inspector {inspector.nombre} {estado} correctamente')
    return redirect('Modulo_admin:inspectores')



@login_required(login_url='Modulo_admin:login_admin')
def eliminar_inspector_view(request, id):
    # Usar all_objects para encontrar incluso inspectores eliminados
    inspector = get_object_or_404(Inspector.all_objects, id=id)
    
    # Marcar como eliminado en lugar de eliminar físicamente
    inspector.is_deleted = True
    inspector.deleted_at = timezone.now()
    inspector.save()
    
    messages.success(request, 'Inspector eliminado correctamente')
    return redirect('Modulo_admin:inspectores')




#Alumnos
@login_required(login_url='Modulo_admin:login_admin')
def alumnos_view(request):

    print("Número total de alumnos:", Alumno.objects.count())

    queryset = Alumno.objects.all().order_by('nombre')
    
    # Iniciar con todos los alumnos no eliminados
    alumnos = Alumno.objects.all()
    cursos = Curso.objects.all()


    # Obtener parámetros de filtrado
    busqueda = request.GET.get('busqueda', '')
    curso_filtro = request.GET.get('curso', '')
    curso_nombre = ""
    
    # Aplicar búsqueda por nombre o RUT si se proporciona
    if busqueda:
        # Limpiar el RUT para la búsqueda (quitar puntos y guiones)
        busqueda_rut = busqueda.replace('.', '').replace('-', '')
        alumnos = alumnos.filter(
            Q(nombre__icontains=busqueda) | 
            Q(rut__icontains=busqueda_rut)
        )
    
    # Filtrar por curso si se proporciona
    if curso_filtro:
        try:
            # Obtener el objeto curso para mostrar su nombre en los filtros activos
            curso_obj = Curso.objects.get(id=curso_filtro)
            curso_nombre = curso_obj.nombre
            # Filtrar alumnos por el curso seleccionado
            alumnos = alumnos.filter(curso__id=curso_filtro)
        except Curso.DoesNotExist:
            pass


    paginator = Paginator(alumnos, 35)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_registros=queryset.count()

    # Después de paginar
    print("Alumnos en la página actual:", len(page_obj))
    print("Número de página:", page_obj.number)
    print("Total de páginas:", page_obj.paginator.num_pages)
        
    
    # Después de aplicar filtros
    print("Alumnos después de filtros:", queryset.count())
    form = AlumnoForm()
    familiar_form = FamiliarForm()
    
    context = {
        'alumnos': page_obj,
        'form': form,
        'familiar_form': familiar_form,
        'busqueda': busqueda,
        'curso_filtro': curso_filtro,
        'cursos': cursos,
        'curso_nombre': curso_nombre,
        'total_registros': total_registros,
        'page_obj': page_obj
    }
    
    return render(request, 'alumnos_folder/estudiantes_folder/tabla_estudiantes.html', context)




@login_required(login_url='Modulo_admin:login_admin')
def registrar_alumno(request):
    """Vista para registrar un nuevo alumno."""
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            # Verificar si ya existe un alumno con ese RUT
            rut = form.cleaned_data['rut']
            if Alumno.objects.filter(rut=rut).exists():
                messages.error(request, f'Ya existe un alumno registrado con el RUT {rut}')
                return redirect('Modulo_admin:alumnos')
            
            # Guardar el nuevo alumno
            alumno = form.save()
            messages.success(request, f'Alumno {alumno.nombre} registrado correctamente')
        else:
            # Si el formulario no es válido, mostrar errores
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en el campo {field}: {error}')
    return redirect('Modulo_admin:alumnos')




def editar_alumno(request, id):
    """Vista para editar un alumno existente."""
    alumno = get_object_or_404(Alumno, id=id)
    
    if request.method == 'POST':
        current_page = request.POST.get('current_page', '1')
        busqueda = request.POST.get('busqueda', '')
        curso_filtro = request.POST.get('curso_filtro', '')

        # Construir la URL de redirección con todos los parámetros
        redirect_url = reverse("Modulo_admin:alumnos")
        params = []
        
        if current_page:
            params.append(f'page={current_page}')
        if busqueda:
            params.append(f'busqueda={busqueda}')
        if curso_filtro:
            params.append(f'curso={curso_filtro}')
        
        if params:
            redirect_url += '?' + '&'.join(params)

        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            # Verificar si el RUT ya existe para otro alumno
            rut = form.cleaned_data['rut']
            if Alumno.objects.filter(rut=rut).exclude(id=id).exists():
                messages.error(request, f'Ya existe otro alumno registrado con el RUT {rut}')
                return redirect('Modulo_admin:alumnos')
            alumno_actualizado = form.save(commit=False)

            # Actualizar información de familiares si se proporcionó
            # Familiar 1
            familiar1_nombre = request.POST.get('familiar_1', '')
            familiar1_rut = request.POST.get('rut_familiar_1', '')
            familiar1_relacion = request.POST.get('familiar_1_relacion', '')
            familiar1_telefono = request.POST.get('familiar_1_telefono', '')
            
            if familiar1_nombre:
                alumno_actualizado.familiar_1 = familiar1_nombre
                alumno_actualizado.rut_familiar_1 = familiar1_rut
                alumno_actualizado.familiar_1_relacion = familiar1_relacion
                alumno_actualizado.familiar_1_telefono = familiar1_telefono
            
            # Familiar 2
            familiar2_nombre = request.POST.get('familiar_2', '')
            familiar2_rut = request.POST.get('rut_familiar_2', '')
            familiar2_relacion = request.POST.get('familiar_2_relacion', '')
            familiar2_telefono = request.POST.get('familiar_2_telefono', '')
            
            if familiar2_nombre:
                alumno_actualizado.familiar_2 = familiar2_nombre
                alumno_actualizado.rut_familiar_2 = familiar2_rut
                alumno_actualizado.familiar_2_relacion = familiar2_relacion
                alumno_actualizado.familiar_2_telefono = familiar2_telefono

            # Guardar los cambios
            alumno_actualizado.save()
            messages.success(request, f'Alumno {alumno.nombre} actualizado correctamente')
            
            return redirect(redirect_url)
              
        else:
            # Si el formulario no es válido, mostrar errores
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en el campo {field}: {error}')
            
            # También redirigir a la misma página en caso de error
            return redirect(redirect_url)
    
    # Si la solicitud no es POST, redirigir a la lista de alumnos
    return redirect('Modulo_admin:alumnos')




@login_required(login_url='Modulo_admin:login_admin')
def eliminar_alumno(request, id):
    """Vista para eliminar un alumno."""
    alumno = get_object_or_404(Alumno, id=id)
    nombre = alumno.nombre
    
    alumno.delete()

    messages.success(request, f'Alumno {nombre} eliminado correctamente')
    return redirect('Modulo_admin:alumnos')




@login_required(login_url='Modulo_admin:login_admin')
def agregar_familiar(request, id, familiar_num):
    """Vista para agregar un familiar a un alumno."""
    alumno = get_object_or_404(Alumno, id=id)
    
    if request.method == 'POST':
        form = FamiliarForm(request.POST)
        if form.is_valid():
            familiar_nombre = form.cleaned_data['familiar_nombre']
            familiar_relacion = form.cleaned_data['familiar_relacion']
            familiar_telefono = form.cleaned_data['familiar_telefono']
            familiar_rut = form.cleaned_data['familiar_rut']
            
            # Actualizar el familiar correspondiente
            if familiar_num == 1:
                alumno.familiar_1 = familiar_nombre
                alumno.familiar_1_relacion = familiar_relacion
                alumno.familiar_1_telefono = familiar_telefono
                alumno.rut_familiar_1 = familiar_rut
                mensaje = f'Familiar 1 agregado correctamente para {alumno.nombre}'
            elif familiar_num == 2:
                alumno.familiar_2 = familiar_nombre
                alumno.familiar_2_relacion = familiar_relacion
                alumno.familiar_2_telefono = familiar_telefono
                alumno.rut_familiar_2 = familiar_rut
                mensaje = f'Familiar 2 agregado correctamente para {alumno.nombre}'
            
            # Guardar los cambios
            alumno.save()
            messages.success(request, mensaje)
        else:
            # Si el formulario no es válido, mostrar errores
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en el campo {field}: {error}')
    
    return redirect('Modulo_admin:alumnos')



@login_required(login_url='Modulo_admin:login_admin')
def retiros_view(request):
    # Iniciar con todos los retiros
    retiros = RegistroRetiro.objects.all().order_by('-hora_retiro')
    cursos = Curso.objects.all()

    queryset = RegistroRetiro.objects.all().order_by('-hora_retiro')

    # Obtener parámetros de filtrado
    busqueda = request.GET.get('busqueda', '')
    curso_filtro = request.GET.get('curso', '')
    curso_nombre = ""
    
    # Aplicar búsqueda por nombre o RUT si se proporciona
    if busqueda:
        # Limpiar el RUT para la búsqueda (quitar puntos y guiones)
        busqueda_rut = busqueda.replace('.', '').replace('-', '')
        retiros = retiros.filter(
            Q(nombre_estudiante__icontains=busqueda) | 
            Q(rut_estudiante__icontains=busqueda_rut) |
            Q(nombre_persona_retira__icontains=busqueda) |
            Q(rut_persona_retira__icontains=busqueda_rut)
        )
    
    # Filtrar por curso si se proporciona
    if curso_filtro:
        try:
            # Obtener el objeto curso para mostrar su nombre en los filtros activos
            curso_obj = Curso.objects.get(id=curso_filtro)
            curso_nombre = curso_obj.nombre
            
            # Filtrar retiros por el curso seleccionado
            retiros_exactos= retiros.filter (curso__iexact = curso_obj.nombre)

            if retiros_exactos.exists():
                retiros = retiros_exactos
            else:
                numero_match = re.search(r'(\d+[°º]?)', curso_obj.nombre)
                numero_curso = numero_match.group(1) if numero_match else None
                nivel_match = re.search(r'[°º]?\s*([A-Za-zÁ-Úá-ú]+)', curso_obj.nombre)
                nivel_curso = nivel_match.group(1) if nivel_match else None

                if numero_curso and nivel_curso:
                    retiros = retiros.filter(Q(curso__icontains=numero_curso) & Q(curso__icontains=nivel_curso))
                else:
                    retiros = retiros.filter(curso__icontains = curso_obj.nombre)
        except Curso.DoesNotExist:
            pass


    paginator = Paginator(retiros, 35)
    page_number = request.GET.get('page')
    page_obj =  paginator.get_page(page_number)
    
    context = {
        'retiros': page_obj,
        'busqueda': busqueda,
        'curso_filtro': curso_filtro,
        'cursos': cursos,
        'curso_nombre': curso_nombre,
        'total_registros': retiros.count(),
        'page_obj':page_obj
    }
    
    return render(request, 'alumnos_folder/retiros_folder/tabla_retiros.html', context)



@login_required(login_url='Modulo_admin:login_admin')
def justificativos_view(request):
    return render(request, 'alumnos_folder/justificativos_folder/tabla_justificativos.html')


@login_required(login_url='Modulo_admin:login_admin')
def grafico_alumnos_view(request):
    # Obtener todos los cursos
    cursos = Curso.objects.all().values_list('nombre', flat=True)
    cursos_list = [c for c in cursos]  # Mantener los nombres originales
    
    # Obtener datos de retiros desde el modelo RegistroRetiro
    from Modulo_alumnos.models import RegistroRetiro
    from django.db.models import Count
    
    # Obtener parámetros de filtrado
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    cursos_filtro = request.GET.get('cursos', '')
    
    # Iniciar con todos los retiros
    retiros = RegistroRetiro.objects.all()
    
    # Agregar logs para depuración
    print(f"Total de retiros encontrados: {retiros.count()}")
    
    # Aplicar filtros si se proporcionan
    if fecha_inicio:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            retiros = retiros.filter(hora_retiro__date__gte=fecha_inicio_obj)
        except ValueError:
            pass
            
    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            # Ajustar fecha_fin para incluir todo el día
            fecha_fin_obj = datetime.combine(fecha_fin_obj, datetime.max.time())
            retiros = retiros.filter(hora_retiro__date__lte=fecha_fin_obj)
        except ValueError:
            pass
    
    if cursos_filtro:
        cursos_lista = cursos_filtro.split(',')
        # Buscar coincidencias parciales para los cursos
        query = Q()
        for curso in cursos_lista:
            query |= Q(curso__icontains=curso)
        retiros = retiros.filter(query)
    
    # Función para clasificar un curso en su nivel educativo
    def clasificar_nivel(curso):
        curso_lower = curso.lower()
        if 'pre-kinder' in curso_lower or 'kinder' in curso_lower:
            return 'Pre-Básica'
        elif 'básico' in curso_lower or 'basico' in curso_lower or any(f"{i}°" in curso for i in range(1, 9)):
            return 'Básica'
        else:
            return 'Media'
    
    # Contar retiros por curso
    retiros_por_curso = retiros.values('curso').annotate(total=Count('id'))
    
    # Agregar logs para depuración
    print(f"Retiros por curso: {list(retiros_por_curso)}")
    
    # Contar retiros por motivo
    retiros_por_motivo = retiros.values('motivo_retiro').annotate(total=Count('id'))
    
    # Preparar datos para el gráfico
    datos_retiros = {}
    
    # Contar retiros por nivel educativo
    niveles = {
        'Pre-Básica': 0,
        'Básica': 0,
        'Media': 0
    }
    
    # Procesar los datos de retiros por curso para agruparlos por nivel
    for item in retiros_por_curso:
        curso = item['curso']
        total = item['total']
        nivel = clasificar_nivel(curso)
        niveles[nivel] += total
        
        # Guardar también el total por curso
        if 'por_curso' not in datos_retiros:
            datos_retiros['por_curso'] = {}
        datos_retiros['por_curso'][curso] = total
    
    datos_retiros['por_nivel'] = niveles
    
    # Procesar los datos de retiros por motivo
    datos_retiros['por_motivo'] = {item['motivo_retiro']: item['total'] for item in retiros_por_motivo}
    
    # Agregar logs para depuración
    print(f"Datos procesados: {datos_retiros}")
    
    # Convertir a JSON para pasar al template
    import json
    datos_retiros_json = json.dumps(datos_retiros)
    cursos_json = json.dumps(cursos_list)

    context = {
        'datos_retiros': datos_retiros_json,
        'cursos': cursos_json
    }
    
    return render(request, 'alumnos_folder/grafico_folder/grafico.html', context)

# BOTON ABANZAR DE AÑO
def promocion_anual_view(request):
    """Vista para realizar la promoción anual de todos los alumnos."""
    if request.method != 'POST':
        messages.error(request, 'Método no permitido')
        return redirect('Modulo_admin:alumnos')
    
    # Verificar si se está solicitando solo la validación
    is_validation_only = request.POST.get('validation_only') == 'true'
    
    try:
        # 1. Obtener todos los cursos actuales
        cursos_actuales = Curso.objects.all()
        cursos_necesarios = []
        
        # 2. Verificar qué cursos serían necesarios para la promoción
        for curso in cursos_actuales:
            alumnos_curso = Alumno.objects.filter(curso=curso)
            if not alumnos_curso.exists():
                continue  # Ignorar cursos sin alumnos
                
            # Extraer información del nombre del curso
            curso_info = curso.nombre.strip()
            
            # Detectar si es Pre-Kinder, Kinder, Básica o Media
            if "Pre-Kinder" in curso_info:
                # Extraer la letra de sección
                letra_match = re.search(r'Pre-Kinder\s+([A-Z])', curso_info)
                letra = letra_match.group(1) if letra_match else ""
                
                # Pre-Kinder a Kinder
                nuevo_nivel = "Kinder"
                nuevo_nombre = f"{nuevo_nivel} {letra}".strip()
                
                # Verificar si el curso ya existe
                if not Curso.objects.filter(nombre__exact=nuevo_nombre).exists():
                    cursos_necesarios.append({
                        'nombre': nuevo_nombre,
                        'nivel': "Pre-basica"
                    })
                
            elif "Kinder" in curso_info and "Pre-Kinder" not in curso_info:
                # Extraer la letra de sección
                letra_match = re.search(r'Kinder\s+([A-Z])', curso_info)
                letra = letra_match.group(1) if letra_match else ""
                
                # Kinder a 1° Básico
                nuevo_nivel = "1° Básico"
                nuevo_nombre = f"{nuevo_nivel} {letra}".strip()
                
                # Verificar si el curso ya existe
                if not Curso.objects.filter(nombre__exact=nuevo_nombre).exists():
                    cursos_necesarios.append({
                        'nombre': nuevo_nombre,
                        'nivel': "Basica"
                    })
                
            elif "Básico" in curso_info or "Basico" in curso_info:
                # Extraer el número de básico
                match = re.search(r'(\d+)°?\s*[Bb][aá]sico', curso_info)
                if match:
                    nivel_actual = int(match.group(1))
                    
                    # Extraer la letra de sección
                    letra_match = re.search(r'[Bb][aá]sico\s+([A-Z])', curso_info)
                    letra = letra_match.group(1) if letra_match else ""
                    
                    if nivel_actual < 8:
                        # 1°-7° Básico pasan al siguiente básico
                        nuevo_nivel = f"{nivel_actual + 1}° Básico"
                        nuevo_nombre = f"{nuevo_nivel} {letra}".strip()
                        
                        # Verificar si el curso ya existe
                        if not Curso.objects.filter(nombre__exact=nuevo_nombre).exists():
                            cursos_necesarios.append({
                                'nombre': nuevo_nombre,
                                'nivel': "Basica"
                            })
                    
                    elif nivel_actual == 8:
                        # 8° Básico pasa a 1° Medio
                        nuevo_nivel = "1° Medio"
                        nuevo_nombre = f"{nuevo_nivel} {letra}".strip()
                        
                        # Verificar si el curso ya existe
                        if not Curso.objects.filter(nombre__exact=nuevo_nombre).exists():
                            cursos_necesarios.append({
                                'nombre': nuevo_nombre,
                                'nivel': "Media"
                            })
            
            elif "Medio" in curso_info:
                # Extraer el número de medio
                match = re.search(r'(\d+)°?\s*[Mm]edio', curso_info)
                if match:
                    nivel_actual = int(match.group(1))
                    
                    # Extraer la letra de sección
                    letra_match = re.search(r'[Mm]edio\s+([A-Z])', curso_info)
                    letra = letra_match.group(1) if letra_match else ""
                    
                    if nivel_actual < 4:
                        # 1°-3° Medio pasan al siguiente medio
                        nuevo_nivel = f"{nivel_actual + 1}° Medio"
                        nuevo_nombre = f"{nuevo_nivel} {letra}".strip()
                        
                        # Verificar si el curso ya existe
                        if not Curso.objects.filter(nombre__exact=nuevo_nombre).exists():
                            cursos_necesarios.append({
                                'nombre': nuevo_nombre,
                                'nivel': "Media"
                            })
        
        # Si solo estamos validando, devolver la lista de cursos necesarios
        if is_validation_only:
            return JsonResponse({
                'success': len(cursos_necesarios) == 0,
                'cursos_necesarios': cursos_necesarios
            })
        
        # Si hay cursos necesarios, no permitir la promoción
        if cursos_necesarios:
            mensaje = "No se puede realizar la promoción anual porque faltan los siguientes cursos: "
            mensaje += ", ".join([curso['nombre'] for curso in cursos_necesarios])
            messages.error(request, mensaje)
            return redirect('Modulo_admin:alumnos')
        
        # Si no hay cursos necesarios, proceder con la promoción
        with transaction.atomic():  # Usar transacción para asegurar integridad
            # 1. Obtener todos los alumnos agrupados por curso
            cursos = Curso.objects.all()
            año_actual = datetime.now().year
            
            # Crear un diccionario para almacenar los alumnos que ya han sido procesados
            alumnos_procesados = set()
            
            # 2. Procesar cada curso
            for curso in cursos:
                # Obtener alumnos que aún no han sido procesados
                alumnos_curso = Alumno.objects.filter(curso=curso)
                if not alumnos_curso.exists():
                    continue  # Ignorar cursos sin alumnos
                
                # Extraer información del nombre del curso
                curso_info = curso.nombre.strip()
                
                # Detectar si es Pre-Kinder, Kinder, Básica o Media
                if "Pre-Kinder" in curso_info:
                    # Extraer la letra de sección
                    letra_match = re.search(r'Pre-Kinder\s+([A-Z])', curso_info)
                    letra = letra_match.group(1) if letra_match else ""
                    
                    # Pre-Kinder a Kinder
                    nuevo_nivel = "Kinder"
                    nuevo_nombre = f"{nuevo_nivel} {letra}".strip()
                    
                    # Buscar el curso (ya sabemos que existe)
                    try:
                        nuevo_curso = Curso.objects.get(nombre__exact=nuevo_nombre)
                        
                        # Actualizar alumnos
                        for alumno in alumnos_curso:
                            # Verificar si el alumno ya fue procesado
                            if alumno.id in alumnos_procesados:
                                continue
                                
                            alumno.curso = nuevo_curso
                            alumno.save()
                            alumnos_procesados.add(alumno.id)
                    except Curso.DoesNotExist:
                        # Si por alguna razón el curso no existe, lanzar error
                        raise Exception(f'No se encontró el curso "{nuevo_nombre}"')
                
                elif "Kinder" in curso_info and "Pre-Kinder" not in curso_info:
                    # Extraer la letra de sección
                    letra_match = re.search(r'Kinder\s+([A-Z])', curso_info)
                    letra = letra_match.group(1) if letra_match else ""
                    
                    # Kinder a 1° Básico
                    nuevo_nivel = "1° Básico"
                    nuevo_nombre = f"{nuevo_nivel} {letra}".strip()
                    
                    # Buscar el curso (ya sabemos que existe)
                    try:
                        nuevo_curso = Curso.objects.get(nombre__exact=nuevo_nombre)
                        
                        # Actualizar alumnos
                        for alumno in alumnos_curso:
                            # Verificar si el alumno ya fue procesado
                            if alumno.id in alumnos_procesados:
                                continue
                                
                            alumno.curso = nuevo_curso
                            alumno.save()
                            alumnos_procesados.add(alumno.id)
                    except Curso.DoesNotExist:
                        # Si por alguna razón el curso no existe, lanzar error
                        raise Exception(f'No se encontró el curso "{nuevo_nombre}"')
                
                elif "Básico" in curso_info or "Basico" in curso_info:
                    # Extraer el número de básico
                    match = re.search(r'(\d+)°?\s*[Bb][aá]sico', curso_info)
                    if match:
                        nivel_actual = int(match.group(1))
                        
                        # Extraer la letra de sección
                        letra_match = re.search(r'[Bb][aá]sico\s+([A-Z])', curso_info)
                        letra = letra_match.group(1) if letra_match else ""
                        
                        if nivel_actual < 8:
                            # 1°-7° Básico pasan al siguiente básico
                            nuevo_nivel = f"{nivel_actual + 1}° Básico"
                            nuevo_nombre = f"{nuevo_nivel} {letra}".strip()
                            
                            # Buscar el curso (ya sabemos que existe)
                            try:
                                nuevo_curso = Curso.objects.get(nombre__exact=nuevo_nombre)
                                
                                # Actualizar alumnos
                                for alumno in alumnos_curso:
                                    # Verificar si el alumno ya fue procesado
                                    if alumno.id in alumnos_procesados:
                                        continue
                                        
                                    alumno.curso = nuevo_curso
                                    alumno.save()
                                    alumnos_procesados.add(alumno.id)
                            except Curso.DoesNotExist:
                                # Si por alguna razón el curso no existe, lanzar error
                                raise Exception(f'No se encontró el curso "{nuevo_nombre}"')
                        
                        elif nivel_actual == 8:
                            # 8° Básico pasa a 1° Medio
                            nuevo_nivel = "1° Medio"
                            nuevo_nombre = f"{nuevo_nivel} {letra}".strip()
                            
                            # Buscar el curso (ya sabemos que existe)
                            try:
                                nuevo_curso = Curso.objects.get(nombre__exact=nuevo_nombre)
                                
                                # Actualizar alumnos
                                for alumno in alumnos_curso:
                                    # Verificar si el alumno ya fue procesado
                                    if alumno.id in alumnos_procesados:
                                        continue
                                        
                                    alumno.curso = nuevo_curso
                                    alumno.save()
                                    alumnos_procesados.add(alumno.id)
                            except Curso.DoesNotExist:
                                # Si por alguna razón el curso no existe, lanzar error
                                raise Exception(f'No se encontró el curso "{nuevo_nombre}"')
                
                elif "Medio" in curso_info:
                    # Extraer el número de medio
                    match = re.search(r'(\d+)°?\s*[Mm]edio', curso_info)
                    if match:
                        nivel_actual = int(match.group(1))
                        
                        # Extraer la letra de sección
                        letra_match = re.search(r'[Mm]edio\s+([A-Z])', curso_info)
                        letra = letra_match.group(1) if letra_match else ""
                        
                        if nivel_actual < 4:
                            # 1°-3° Medio pasan al siguiente medio
                            nuevo_nivel = f"{nivel_actual + 1}° Medio"
                            nuevo_nombre = f"{nuevo_nivel} {letra}".strip()
                            
                            # Buscar el curso (ya sabemos que existe)
                            try:
                                nuevo_curso = Curso.objects.get(nombre__exact=nuevo_nombre)
                                
                                # Actualizar alumnos
                                for alumno in alumnos_curso:
                                    # Verificar si el alumno ya fue procesado
                                    if alumno.id in alumnos_procesados:
                                        continue
                                        
                                    alumno.curso = nuevo_curso
                                    alumno.save()
                                    alumnos_procesados.add(alumno.id)
                            except Curso.DoesNotExist:
                                # Si por alguna razón el curso no existe, lanzar error
                                raise Exception(f'No se encontró el curso "{nuevo_nombre}"')
                        
                        elif nivel_actual == 4:
                            # 4° Medio pasa a Egresados
                            for alumno in alumnos_curso:
                                # Verificar si el alumno ya fue procesado
                                if alumno.id in alumnos_procesados:
                                    continue
                                    
                                # Crear registro de alumno egresado
                                AlumnoEgresado.objects.create(
                                    rut=alumno.rut,
                                    nombre=alumno.nombre,
                                    ultimo_curso=curso.nombre,
                                    apoderado_titular=alumno.apoderado_titular,
                                    rut_apoderadoT=alumno.rut_apoderadoT,
                                    telefono_apoderadoT=alumno.telefono_apoderadoT,
                                    apoderado_suplente=alumno.apoderado_suplente,
                                    rut_apoderadoS=alumno.rut_apoderadoS,
                                    telefono_apoderadoS=alumno.telefono_apoderadoS,
                                    familiar_1=alumno.familiar_1,
                                    familiar_1_relacion=alumno.familiar_1_relacion,
                                    familiar_1_telefono=alumno.familiar_1_telefono,
                                    rut_familiar_1=alumno.rut_familiar_1,
                                    familiar_2=alumno.familiar_2,
                                    familiar_2_relacion=alumno.familiar_2_relacion,
                                    familiar_2_telefono=alumno.familiar_2_telefono,
                                    rut_familiar_2=alumno.rut_familiar_2,
                                    año_egreso=año_actual
                                )
                                
                                # Eliminar el alumno de la tabla de alumnos activos
                                alumno.delete()
                                alumnos_procesados.add(alumno.id)
            
            # Registrar la acción en el log
            messages.success(request, f'Promoción anual completada exitosamente. Los alumnos han sido promovidos al siguiente año académico.')
            return redirect('Modulo_admin:alumnos')
    
    except Exception as e:
        messages.error(request, f'Error al realizar la promoción anual: {str(e)}')
        return redirect('Modulo_admin:alumnos')
    

@login_required(login_url='Modulo_admin:login_admin')
def alumnos_egresados_view(request):
    """Vista para mostrar la lista de alumnos egresados."""
    # Obtener el año de filtro si existe
    año_filtro = request.GET.get('año')
    
    # Filtrar los egresados según el año seleccionado
    if año_filtro:
        try:
            año_filtro = int(año_filtro)
            egresados = AlumnoEgresado.objects.filter(año_egreso=año_filtro)
        except ValueError:
            # Si el año no es un número válido, mostrar todos
            egresados = AlumnoEgresado.objects.all()
    else:
        # Si no hay filtro, mostrar todos
        egresados = AlumnoEgresado.objects.all()
    
    # Obtener todos los años de egreso disponibles para el filtro
    años_egreso = AlumnoEgresado.objects.values_list('año_egreso', flat=True).distinct().order_by('-año_egreso')
    
    context = {
        'egresados': egresados,
        'años_egreso': años_egreso,
        'año_filtro': año_filtro
    }
    
    return render(request, 'alumnos_folder/estudiantes_folder/alumnos_egresados.html', context)