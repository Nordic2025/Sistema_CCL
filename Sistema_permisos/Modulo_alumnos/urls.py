from django.urls import path
from . import views

app_name = 'Modulo_alumnos'
urlpatterns = [
    path('retiro_justificacion/', views.retiro_justificacion_view, name='retiro_justificacion'),
]