# Generated by Django 4.2.16 on 2025-04-16 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Modulo_admin', '0010_merge_20250416_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumno',
            name='curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Modulo_admin.curso'),
        ),
    ]
