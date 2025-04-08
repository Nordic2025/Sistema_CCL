from django.urls import path
from . import views

app_name = 'Modulo_admin'

urlpatterns = [
    path('admin/', views.loginadmin_view, name='admin'),  
    path('login/', views.login_admin, name='login_admin'),
    path('logout/', views.logout_admin, name='logout_admin'),
    path('grafico/', views.graficoview, name='grafico'),
    path('historial_permisos/', views.tabla_generalview, name='historial_permisos'),
    path('hsitorial_salidas/', views.tabla_salidasview, name='historial_salidas'),
   
    path('exportar_permisos_pdf/', views.exportar_permisos_pdf, name='exportar_permisos_pdf'),
    path('exportar_salidas_pdf/', views.exportar_salidas_pdf, name='exportar_salidas_pdf'),

    path('exportar-permisos-pdf/', views.exportar_permisos_pdf, name='exportar_permisos_pdf'),
    path('exportar-salidas-pdf/', views.exportar_salidas_pdf, name='exportar_salidas_pdf'),

    path('administrador/', views.administradores_view, name='administradores'),
    path('registrar_administrador/', views.registrar_administrador_view, name='registrar_administrador'),
    path('editar_administrador/<int:id>/', views.editar_administrador_view, name='editar_administrador'),
    path('eliminar_administrador/<int:id>/', views.eliminar_administrador_view, name='eliminar_administrador'),
    path('area/', views.areas_view, name='area'),
    path('agregar_area/', views.registrar_areas_view, name='agregar_area'),
    path('editar_areas/<int:id>/', views.editar_areas_view, name='editar_area'),
    path('eliminar_areas/<int:id>/', views.eliminar_areas_view, name='eliminar_area'),
    path('historial_salidas/', views.tabla_salidasview, name='historial_salidas'),
]

