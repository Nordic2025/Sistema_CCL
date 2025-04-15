from django.urls import path
from . import views

app_name = 'Modulo_alumnos'
urlpatterns = [
    path('retiro_justificacion/', views.retiro_justificacion_view, name='retiro_justificacion'),
    path('formulario_retiro/', views.formulario_retiro_view, name='formulario_retiro'),
    path('formulario_justificar/', views.formulario_justificacion_view, name='formulario_justificacion'),
    path('confirmar_retiro/<int:registro_id>/', views.confirmar_retiro_view, name='confirmar_retiro'),
]
