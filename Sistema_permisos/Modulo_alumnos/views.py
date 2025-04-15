from django.shortcuts import render

# Create your views here.
def retiro_justificacion_view(request):
    return render(request, 'retiro_justificacion.html')