# Generated by Django 4.2.16 on 2025-04-22 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Modulo_admin', '0014_merge_20250416_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='alumno',
            name='numero_apoderadoS',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='alumno',
            name='numero_apoderadoT',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
