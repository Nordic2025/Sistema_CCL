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
    # Opciones para el nivel educativo
    NIVEL_CHOICES = [
        ('Pre-basica', 'Pre-básica'),
        ('Basica', 'Básica'),
        ('Media', 'Media'),
    ]
    
    nombre = models.CharField(max_length=50, verbose_name='Nombre del Curso')
    nivel = models.CharField(
        max_length=20, 
        choices=NIVEL_CHOICES, 
        default='Basica',
        verbose_name='Nivel Educativo'
    )
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de eliminación')
    
    # Managers
    objects = CursoManager()  # Manager predeterminado que filtra cursos eliminados
    all_objects = models.Manager()  # Manager para acceder a todos los cursos, incluso eliminados
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['nivel', 'nombre']

    def __str__(self):
        return f"{self.nombre} - {self.get_nivel_display()}"

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
    
    def get_niveles_asignados(self):
        """Retorna una cadena con los niveles educativos asignados al inspector"""
        niveles = set()
        for curso in self.cursos.all():
            niveles.add(curso.get_nivel_display())
        
        if not niveles:
            return "Sin niveles asignados"
        
        return " - ".join(sorted(niveles))



class Alumno(models.Model):
    rut = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=255)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    apoderado_titular = models.CharField(max_length=255)
    rut_apoderadoT = models.CharField(max_length=15, blank=True, null=True)
    apoderado_suplente = models.CharField(max_length=255, blank=True, null=True)
    rut_apoderadoS = models.CharField(max_length=15, blank=True, null=True)
    familiar_1 = models.CharField(max_length=255, blank=True, null=True)
    familiar_1_relacion = models.CharField(max_length=100, blank=True, null=True)
    familiar_1_telefono = models.CharField(max_length=20, blank=True, null=True)
    rut_familiar_1 = models.CharField(max_length=15, blank=True, null=True)
    familiar_2 = models.CharField(max_length=255, blank=True, null=True)
    familiar_2_relacion = models.CharField(max_length=100, blank=True, null=True)
    familiar_2_telefono = models.CharField(max_length=20, blank=True, null=True)
    rut_familiar_2 = models.CharField(max_length=15, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.nombre} - {self.curso}"

    class Meta:
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"
        ordering = ['curso', 'nombre']

