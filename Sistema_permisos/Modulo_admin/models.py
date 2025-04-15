from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User


class Administrador(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True )
    # Validador para RUT chileno (formato: 12.345.678-9)
    rut_validator = RegexValidator(
        regex=r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]$',
        message='Ingrese un RUT válido en formato XX.XXX.XXX-X'
    )
    
    rut = models.CharField(
        max_length=12, 
        validators=[rut_validator],
        unique=True,
        verbose_name='RUT'
    )
    nombre = models.CharField(max_length=100, verbose_name='Nombre Completo')
    area = models.CharField(max_length=100, verbose_name='Área')
    
    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.area}"
    

class AreasManager(models.Manager):
    def get_queryset(self):
        # Excluir áreas marcadas como eliminadas
        return super().get_queryset().filter(is_deleted=False)
    

class Areas(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    encargado = models.CharField(max_length=100, verbose_name='Encargado')
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de eliminación')
    
    # Managers
    objects = AreasManager()  # Manager predeterminado que filtra áreas eliminadas
    all_objects = models.Manager()  # Manager para acceder a todas las áreas, incluso eliminadas
    
    class Meta:
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.encargado} - {self.nombre}"
    
    
# Agregar al final del archivo

class CursoManager(models.Manager):
    def get_queryset(self):
        # Excluir cursos marcados como eliminados
        return super().get_queryset().filter(is_deleted=False)

class Curso(models.Model):
    nombre = models.CharField(max_length=50, verbose_name='Nombre del Curso')
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de eliminación')
    
    # Managers
    objects = CursoManager()  # Manager predeterminado que filtra cursos eliminados
    all_objects = models.Manager()  # Manager para acceder a todos los cursos, incluso eliminados
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre





#Alumnos
# Add these imports if they're not already present
from django.db import models
from django.contrib.auth.models import User

# Add this model to your existing models.py file
class Alumno(models.Model):
    rut = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=255)
    curso = models.CharField(max_length=50)
    apoderado_titular = models.CharField(max_length=255)
    apoderado_suplente = models.CharField(max_length=255, blank=True, null=True)
    familiar_1 = models.CharField(max_length=255, blank=True, null=True)
    familiar_1_relacion = models.CharField(max_length=100, blank=True, null=True)
    familiar_1_telefono = models.CharField(max_length=20, blank=True, null=True)
    familiar_2 = models.CharField(max_length=255, blank=True, null=True)
    familiar_2_relacion = models.CharField(max_length=100, blank=True, null=True)
    familiar_2_telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.curso}"

    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"
        ordering = ['curso', 'nombre']

