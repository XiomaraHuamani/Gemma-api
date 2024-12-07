# Generated by Django 4.2.16 on 2024-12-06 17:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('locales', '0002_remove_local_subnivel_de'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubnivelRelacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subnivel_1', models.ForeignKey(help_text='Primer subnivel de la zona principal.', on_delete=django.db.models.deletion.CASCADE, related_name='relacion_subnivel_1', to='locales.local')),
                ('subnivel_2', models.ForeignKey(help_text='Segundo subnivel de la zona principal.', on_delete=django.db.models.deletion.CASCADE, related_name='relacion_subnivel_2', to='locales.local')),
                ('zona_principal', models.ForeignKey(help_text='Zona principal que tiene subniveles.', on_delete=django.db.models.deletion.CASCADE, related_name='relaciones_subniveles', to='locales.zona')),
            ],
            options={
                'verbose_name': 'Relación de Subnivel',
                'verbose_name_plural': 'Relaciones de Subniveles',
                'unique_together': {('zona_principal', 'subnivel_1', 'subnivel_2')},
            },
        ),
    ]
