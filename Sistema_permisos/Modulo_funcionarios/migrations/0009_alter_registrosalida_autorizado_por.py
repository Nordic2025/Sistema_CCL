# Generated by Django 4.2.16 on 2025-04-10 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Modulo_admin', '0003_areas'),
        ('Modulo_funcionarios', '0008_registrosalida_duracion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrosalida',
            name='autorizado_por',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='autorizaciones', to='Modulo_admin.areas'),
        ),
    ]
