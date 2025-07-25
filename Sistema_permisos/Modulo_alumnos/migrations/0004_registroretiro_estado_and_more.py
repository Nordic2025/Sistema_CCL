# Generated by Django 4.2.16 on 2025-04-21 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Modulo_alumnos', '0003_registroretiro_nombre_persona_retira'),
    ]

    operations = [
        migrations.AddField(
            model_name='registroretiro',
            name='estado',
            field=models.CharField(choices=[('waiting', 'En Espera'), ('confirmed', 'Confirmado'), ('rejected', 'Rechazado'), ('timeout', 'Tiempo de espera agotado')], default='waiting', max_length=20),
        ),
        migrations.AddField(
            model_name='registroretiro',
            name='mensaje_respuesta',
            field=models.TextField(blank=True, null=True),
        ),
    ]
