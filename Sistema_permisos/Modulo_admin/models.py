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
    
    
# MODELO CURSOS
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

#MODELO INSPECTORES

class InspectorManager(models.Manager):
    def get_queryset(self):
        # Excluir inspectores marcados como eliminados
        return super().get_queryset().filter(is_deleted=False)

class Inspector(models.Model):
    # Validador para RUT chileno (formato: 12.345.678-9)
    rut_validator = RegexValidator(
        regex=r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]$',
        message='Ingrese un RUT válido en formato XX.XXX.XXX-X'
    )
    
    # Validador para número de teléfono
    telefono_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Ingrese un número de teléfono válido. Debe contener entre 9 y 15 dígitos.'
    )
    
    nombre = models.CharField(max_length=100, verbose_name='Nombre Completo')
    rut = models.CharField(
        max_length=12, 
        validators=[rut_validator],
        unique=True,
        verbose_name='RUT'
    )
    telefono = models.CharField(
        max_length=15,
        validators=[telefono_validator],
        verbose_name='Número de Teléfono'
    )
    cursos = models.ManyToManyField(Curso, related_name='inspectores', verbose_name='Cursos a cargo')
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de eliminación')
    
    # Managers
    objects = InspectorManager()  # Manager predeterminado que filtra inspectores eliminados
    all_objects = models.Manager()  # Manager para acceder a todos los inspectores, incluso eliminados
    
    class Meta:
        verbose_name = 'Inspector'
        verbose_name_plural = 'Inspectores'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.rut}"

