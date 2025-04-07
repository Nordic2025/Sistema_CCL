from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import AdministradorForm, AreasForm
from .models import Administrador, Areas
from Modulo_funcionarios.models import RegistroSalida

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
    permisos = RegistroSalida.objects.filter(hora_regreso__isnull=False)
    return render(request, "tabla_general.html", {'permisos': permisos})


# Vista tabla_salidas
@login_required(login_url='Modulo_admin:login_admin')
def tabla_salidasview(request):
    salidas = RegistroSalida.objects.filter(hora_regreso__isnull=True)
    return render(request, "tabla_salidas.html", {'salidas': salidas})


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
