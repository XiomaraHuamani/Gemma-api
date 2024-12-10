# Generated by Django 4.2.16 on 2024-12-10 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locales', '0003_subnivelrelacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='subnivelrelacion',
            name='permitir_zonas_diferentes',
            field=models.BooleanField(default=False, help_text='Permitir que los subniveles estén en zonas diferentes.'),
        ),
    ]
