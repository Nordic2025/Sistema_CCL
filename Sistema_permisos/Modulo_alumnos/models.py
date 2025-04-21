from django.db import models
import uuid
from django.utils.timezone import now
from django.core.validators import RegexValidator

class RegistroRetiro(models.Model):
    # Opciones para el motivo del retiro
    MOTIVO_CHOICES = [
        ('Asuntos Medicos', 'Asuntos Médicos'),
        ('Asuntos Familiares', 'Asuntos Familiares'),
        ('Motivos Personales', 'Motivos Personales'),
        ('Prefiero no decirlo', 'Prefiero no decirlo'),
    ]

    ESTADOS_CHOICES =[
        ('waiting', 'En Espera'),
        ('confirmed', 'Confirmado'),
        ('rejected', 'Rechazado'),
        ('timeout', 'Tiempo de espera agotado'),
    ]

    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='waiting')
    mensaje_respuesta = models.TextField(blank=True, null=True)
    
    # Validador para RUT chileno (formato: 12.345.678-9)
    rut_validator = RegexValidator(
        regex=r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]$',
        message='Ingrese un RUT válido en formato XX.XXX.XXX-X'
    )
    
    rut_persona_retira = models.CharField(max_length=12, validators=[rut_validator], verbose_name='RUT de quien retira')
    nombre_persona_retira = models.CharField(max_length=255, verbose_name='Nombre de quien retira')
    rut_estudiante = models.CharField(max_length=12, validators=[rut_validator], verbose_name='RUT del estudiante')
    nombre_estudiante = models.CharField(max_length=255, verbose_name='Nombre del estudiante')
    curso = models.CharField(max_length=20, verbose_name='Curso')
    inspector_cargo = models.CharField(max_length=255, verbose_name='Inspector a cargo')
    motivo_retiro = models.CharField(max_length=20, choices=MOTIVO_CHOICES, verbose_name='Motivo del retiro')
    hora_retiro = models.DateTimeField(default=now, verbose_name='Fecha y hora del retiro')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_estudiante} - {self.rut_estudiante}"
