# Generated by Django 4.2 on 2024-11-19 09:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_proyecto', models.CharField(help_text='Nombre del proyecto al que está asociado el cliente', max_length=100)),
                ('usuario_credencial', models.CharField(help_text='Nombre de usuario o credencial', max_length=50)),
                ('razon_social', models.CharField(blank=True, help_text='Razón social del cliente si aplica', max_length=255, null=True)),
                ('nombres', models.CharField(help_text='Nombres del cliente', max_length=100)),
                ('apellido_paterno', models.CharField(help_text='Apellido paterno del cliente', max_length=100)),
                ('apellido_materno', models.CharField(help_text='Apellido materno del cliente', max_length=100)),
                ('dni', models.IntegerField(help_text='Documento de identidad del cliente')),
                ('direccion', models.CharField(help_text='Dirección del cliente', max_length=255)),
                ('numero_cel', models.IntegerField(help_text='Número de celular del cliente')),
                ('correo', models.EmailField(help_text='Correo electrónico del cliente', max_length=254)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, help_text='Fecha de creación del registro')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, help_text='Fecha de última actualización del registro')),
            ],
        ),
        migrations.CreateModel(
            name='Local',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.CharField(choices=[('disponible', 'Disponible'), ('separado', 'Separado'), ('vendido', 'Vendido')], default='disponible', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Metraje',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('area', models.CharField(help_text="Área total en metros cuadrados (ejemplo: '12.5 m²')", max_length=50)),
                ('altura', models.CharField(help_text="Altura en metros (ejemplo: '4.5 m')", max_length=50)),
                ('perimetro', models.CharField(help_text="Perímetro en metros (ejemplo: '2.5 x 5')", max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TipoDescuento',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('condiciones', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Zona',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('codigo', models.CharField(help_text='Código único de 10 dígitos para la zona', max_length=10, unique=True)),
                ('linea_base', models.CharField(choices=[('primera_linea', 'Primera Línea'), ('segunda_linea', 'Segunda Línea'), ('tercera_linea', 'Tercera Línea')], default='primera_linea', help_text='Línea base de la zona', max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='ReciboArras',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('numero', models.CharField(max_length=20, unique=True)),
                ('fecha', models.DateField()),
                ('fecha_vencimiento', models.DateField()),
                ('direccion', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('monto_efectivo', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('monto_deposito', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('banco', models.CharField(blank=True, max_length=50, null=True)),
                ('numero_operacion_bancaria', models.CharField(blank=True, max_length=50, null=True)),
                ('proyecto', models.CharField(max_length=100)),
                ('precio_lista', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_final', models.DecimalField(decimal_places=2, max_digits=10)),
                ('condicion', models.CharField(max_length=100)),
                ('plazo', models.CharField(max_length=100)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='locales.cliente')),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='locales.local')),
                ('metraje', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='locales.metraje')),
                ('zona', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='locales.zona')),
            ],
        ),
        migrations.AddField(
            model_name='local',
            name='metraje',
            field=models.ForeignKey(help_text='Rango de metraje del local', on_delete=django.db.models.deletion.CASCADE, to='locales.metraje'),
        ),
        migrations.AddField(
            model_name='local',
            name='zona',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locales', to='locales.zona'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='local',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clientes', to='locales.local'),
        ),
        migrations.CreateModel(
            name='PrecioBase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('precio', models.DecimalField(decimal_places=2, help_text='Precio base para la combinación de zona y metraje', max_digits=10)),
                ('metraje', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='precios_base', to='locales.metraje')),
                ('zona', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='precios_base', to='locales.zona')),
            ],
            options={
                'verbose_name': 'Precio Base',
                'verbose_name_plural': 'Precios Base',
                'unique_together': {('zona', 'metraje')},
            },
        ),
        migrations.CreateModel(
            name='Descuento',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('monto', models.DecimalField(blank=True, decimal_places=2, help_text='Monto de descuento opcional', max_digits=10, null=True)),
                ('porcentaje', models.DecimalField(blank=True, decimal_places=2, help_text='Porcentaje de descuento opcional', max_digits=5, null=True)),
                ('metraje', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descuentos', to='locales.metraje')),
                ('tipo_descuento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descuentos', to='locales.tipodescuento')),
                ('zona', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descuentos', to='locales.zona')),
            ],
            options={
                'verbose_name': 'Descuento',
                'verbose_name_plural': 'Descuentos',
                'unique_together': {('zona', 'metraje', 'tipo_descuento')},
            },
        ),
    ]
