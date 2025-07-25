from django.urls import path
from . import views

app_name = 'Modulo_admin'

urlpatterns = [
    path('admin/', views.loginadmin_view, name='admin'),  
    path('login/', views.login_admin, name='login_admin'),
    path('logout/', views.logout_admin, name='logout_admin'),
    path('inicio/', views.inicio_view, name='inicio'),
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


    path('cambiar_contraseña/<int:id>/', views.cambiar_password_view, name='cambiar_contraseña'),

    #MODULO ALUMNOS / CURSOS

    path('cursos/', views.cursos_view, name='cursos'),
    path('agregar_curso/', views.registrar_curso_view, name='agregar_curso'),
    path('editar_curso/<int:id>/', views.editar_curso_view, name='editar_curso'),
    path('eliminar_curso/<int:id>/', views.eliminar_curso_view, name='eliminar_curso'),  

    #MODULO ALUMNOS / INSPECTORES 

    path('inspectores/', views.inspectores_view, name='inspectores'),
    path('agregar_inspector/', views.registrar_inspector_view, name='agregar_inspector'),
    path('editar_inspector/<int:id>/', views.editar_inspector_view, name='editar_inspector'),
    path('eliminar_inspector/<int:id>/', views.eliminar_inspector_view, name='eliminar_inspector'),
    path('inspectores/cambiar-estado/<int:id>/', views.cambiar_estado_inspector_view, name='cambiar_estado_inspector'),

    path('alumnos/', views.alumnos_view, name='alumnos'),
    path('agregar_alumno/',views.registrar_alumno, name='agregar_alumno'),
    path('editar_alumno/<int:id>/', views.editar_alumno, name='editar_alumno'),
    path('verificar_rut_egresado/', views.verificar_rut_egresado, name='verificar_rut_egresado'),    
   path('agregar_familiares/<int:alumno_id>/<int:familiar_num>/', views.agregar_familiar, name='agregar_familiar'),
    path('alumnos/eliminar-familiar/<int:alumno_id>/<int:familiar_num>/', views.eliminar_familiar, name='eliminar_familiar'),
    path('alumnos/obtener-datos/<int:alumno_id>/', views.obtener_datos_alumno, name='obtener_datos_alumno'),
    
    
    path('retiros/', views.retiros_view, name='retiros'),
    path('confirmar-retiro/<int:retiro_id>/', views.confirmar_retiro, name='confirmar_retiro'),

    path('justificaciones/', views.justificativos_view, name='justificaciones'),
    path('grafico_alumnos/', views.grafico_alumnos_view, name='grafico_alumnos'),

    path('promocion-anual/', views.promocion_anual_view, name='promocion_anual'),
    path('alumnos-egresados/', views.alumnos_egresados_view, name='alumnos_egresados'),
]






