# Generated by Django 4.2.16 on 2024-12-11 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CpInversion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_apellidos', models.CharField(max_length=255)),
                ('correo_electronico', models.EmailField(max_length=254)),
                ('numero_telefono', models.CharField(blank=True, max_length=15, null=True)),
                ('dni', models.CharField(blank=True, max_length=20, null=True)),
                ('tipo_local', models.CharField(choices=[('12.5', '12.5 m²'), ('25', '25 m²'), ('50', '50 m²'), ('300', '300 m²')], max_length=50)),
                ('objetivo_inversion', models.CharField(choices=[('comercial', 'Comercial'), ('inversion', 'Inversión')], max_length=50)),
                ('mensaje', models.TextField(blank=True, null=True)),
                ('acepta_terminos', models.BooleanField()),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
