import uuid
from django.db import models
from django.utils.timezone import now
from django.core.validators import RegexValidator
from Modulo_admin.models import Areas

class RegistroSalida(models.Model):
    # Definimos las opciones para el motivo de salida
    MOTIVO_CHOICES = [
        ('Tramites', 'Trámites'),
        ('Compras', 'Compras'),
        ('Salidas Pedagogicas', 'Salidas Pedagógicas'),
        ('Otros', 'Otros'),
    ]
    
    # Corrección del validador de RUT - el problema estaba en la sintaxis de la expresión regular
    rut_validator = RegexValidator(
        regex=r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]$',  # Corregido el cierre de la expresión regular
        message='Ingrese un RUT válido en formato XX.XXX.XXX-X'
    )

    codigo_registro = models.CharField(max_length=4, unique=True, editable=False)  # Código único
    # Eliminamos cualquier restricción de unicidad en el campo RUT
    rut = models.CharField(
        max_length=12, 
        validators=[rut_validator],
        verbose_name='RUT'
    )  # Rut del funcionario
    nombre = models.CharField(max_length=255)  # Nombre del funcionario
    autorizado_por = models.ForeignKey(Areas, on_delete=models.CASCADE, related_name='autorizaciones')
    area_perteneciente = models.CharField(max_length=100)  # Este campo se llenará automáticamente
    motivo_salida = models.CharField(max_length=20, choices=MOTIVO_CHOICES)  # Motivo de la salida como lista desplegable
    hora_salida = models.DateTimeField(default=now)  # Hora de salida
    hora_regreso = models.DateTimeField(null=True, blank=True)  # Hora de regreso (vacío al principio)
    duracion = models.DurationField(null=True, blank=True)  # Nuevo campo para almacenar la duración

    def save(self, *args, **kwargs):
        # Generar el código único de 4 dígitos si no se ha asignado
        if not self.codigo_registro:
            self.codigo_registro = str(uuid.uuid4().int)[:4]  # Genera un código aleatorio único de 4 dígitos
        
        # Calcular la duración si hay hora de regreso
        if self.hora_regreso and self.hora_salida:
            self.duracion = self.hora_regreso - self.hora_salida
        
        # Guardar el objeto con los valores del formulario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.codigo_registro}"