from django.db import models
from django.core.validators import RegexValidator

class Administrador(models.Model):
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
    


class Areas(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    encargado = models.CharField(max_length=100, verbose_name='Encargado')

    class Meta:
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'
        ordering = ['nombre']

    def __str__(self):
        return  f"{self.encargado} - {self.nombre}"
