from django.urls import path
from . import views

app_name = 'Modulo_funcionarios'
urlpatterns = [
    # Ruta para ingresar al submenu de permisos y regresos
    path('ingreso_salida/', views.ingreso_salida, name='ingreso_salida'),

    # Ruta para registrar permiso
    path('formulario_permisos/', views.registrar_salida, name='formulario_permisos'),

    # Ruta para registrar regreso
    path('formulario_regreso/', views.formulario_regreso, name='formulario_regreso'),

    path('confirmacion-permiso/<int:registro_id>/', views.confirmacion_permiso, name='confirmacion_permiso'),
    # También mantén la URL sin parámetros para compatibilidad
    path('confirmacion-permiso/', views.confirmacion_permiso, name='confirmacion_permiso'),

    path('confirmar-regreso/<str:codigo>/', views.confirmar_regreso, name='confirmar_regreso'),
    
    # Añadir esta ruta para recuperar código
    path('recuperar-codigo/', views.recuperar_codigo, name='recuperar_codigo'),
    
    # Añadir esta ruta para la versión AJAX
    path('recuperar-codigo-ajax/', views.recuperar_codigo_ajax, name='recuperar_codigo_ajax'),

    path('get-area-encargado/', views.get_area_encargado, name='get_area_encargado'),
]

