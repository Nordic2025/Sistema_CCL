# Generated by Django 4.2.16 on 2025-04-28 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Modulo_alumnos', '0004_registroretiro_estado_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registroretiro',
            name='estado',
            field=models.CharField(choices=[('waiting', 'En Espera'), ('confirmed', 'Confirmado'), ('rejected', 'Rechazado'), ('timeout', 'Tiempo de espera agotado'), ('confirmed_busy', 'Ocupado')], default='waiting', max_length=20),
        ),
    ]
