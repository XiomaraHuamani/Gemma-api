# Generated by Django 4.2.16 on 2024-12-10 10:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('locales', '0004_subnivelrelacion_permitir_zonas_diferentes'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='local',
            name='unique_local_per_zona_metraje',
        ),
    ]
