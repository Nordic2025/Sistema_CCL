# Generated by Django 4.2.16 on 2025-04-16 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Modulo_alumnos', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registroretiro',
            name='tipo_persona',
        ),
    ]
