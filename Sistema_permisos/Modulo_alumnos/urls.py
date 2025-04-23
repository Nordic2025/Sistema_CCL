from django.urls import path
from . import views

app_name = 'Modulo_alumnos'
urlpatterns = [
    path('retiro_justificacion/', views.retiro_justificacion_view, name='retiro_justificacion'),
    path('formulario_retiro/', views.formulario_retiro_view, name='formulario_retiro'),
    path('formulario_justificacion/', views.formulario_justificacion_view, name='formulario_justificacion'),
    path('confirmacion_retiro/<int:registro_id>/', views.confirmacion_retiro_view, name='confirmacion_retiro'),
    path('verificar-apoderado/', views.verificar_apoderado, name='verificar_apoderado'),
    path('obtener-datos-alumno/', views.obtener_datos_alumno, name='obtener_datos_alumno'),
    path('procesar-retiro/', views.procesar_retiro, name='procesar_retiro'),
    path('verificar-estado-retiro/', views.verificar_estado_retiro, name='verificar_estado_retiro'),
    path('actualizar-estado-retiro/', views.actualizar_estado_retiro, name='actualizar_estado_retiro'),
]
