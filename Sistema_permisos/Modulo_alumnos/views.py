from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import RegistroRetiro
from .forms import RegistroRetiroForm

# Create your views here.
def retiro_justificacion_view(request):
    return render(request, 'retiro_justificacion.html')

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

def confirmar_retiro_view(request, registro_id):
    registro = RegistroRetiro.objects.get(id=registro_id)
    return render(request, 'confirmar_retiro.html', {'registro': registro})

def formulario_justificacion_view(request):
    return render(request, 'formulario_justificar.html')