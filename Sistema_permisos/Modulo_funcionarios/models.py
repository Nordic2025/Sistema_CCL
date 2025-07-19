import uuid
from django.db import models
from django.utils.timezone import now
from django.core.validators import RegexValidator
from Modulo_admin.models import Areas

class RegistroSalida(models.Model):
    # Opciones para el motivo de salida
    MOTIVO_CHOICES = [
        ('Tramites', 'Trámites'),
        ('Compras', 'Compras'),
        ('Salidas Pedagogicas', 'Salidas Pedagógicas'),
        ('Otros', 'Otros'),
    ]
    
    rut_validator = RegexValidator(
        regex=r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]$', 
        message='Ingrese un RUT válido en formato XX.XXX.XXX-X'
    )

    codigo_registro = models.CharField(max_length=5, unique=True, editable=False)  
    rut = models.CharField(
        max_length=12, 
        validators=[rut_validator],
        verbose_name='RUT'
    )  # Rut del funcionario
    nombre = models.CharField(max_length=255)  # Nombre del funcionario
    autorizado_por = models.ForeignKey(Areas, on_delete=models.DO_NOTHING, related_name='autorizaciones')
    area_perteneciente = models.CharField(max_length=100)  # Área a la que pertenece (Se llena automáticamente)
    motivo_salida = models.CharField(max_length=20, choices=MOTIVO_CHOICES)  # Motivo de la salida
    hora_salida = models.DateTimeField(default=now)  # Hora de salida
    hora_regreso = models.DateTimeField(null=True, blank=True)  # Hora de regreso
    duracion = models.DurationField(null=True, blank=True)  # Duración de la salida

    def save(self, *args, **kwargs):
        if not self.codigo_registro:
            self.codigo_registro = str(uuid.uuid4().int)[:5]  # Genera un código aleatorio único de 4 dígitos
        
        if self.hora_regreso and self.hora_salida:
            self.duracion = self.hora_regreso - self.hora_salida
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.codigo_registro}"