# Generated by Django 4.2.16 on 2024-12-20 20:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(help_text='Nombre único para la categoría de zona', max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Descuento',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('monto', models.DecimalField(blank=True, decimal_places=2, help_text='Monto de descuento opcional', max_digits=10, null=True)),
                ('porcentaje', models.DecimalField(blank=True, decimal_places=2, help_text='Porcentaje de descuento opcional', max_digits=5, null=True)),
                ('categoria', models.ForeignKey(help_text='Categoría asociada al descuento', on_delete=django.db.models.deletion.PROTECT, related_name='descuentos', to='locales.categoria')),
            ],
            options={
                'verbose_name': 'Descuento',
                'verbose_name_plural': 'Descuentos',
            },
        ),
        migrations.CreateModel(
            name='Local',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.CharField(choices=[('disponible', 'Disponible'), ('reservado', 'Reservado'), ('vendido', 'Vendido')], default='Disponible', help_text='Estado del local (disponible, reservado, vendido).', max_length=20)),
                ('tipo', models.CharField(blank=True, choices=[('entrada segundaria grupo 1 izquierda', 'Entrada segundaria grupo 1 izquierda'), ('entrada segundaria grupo 1 derecha', 'Entrada segundaria grupo 1 derecha'), ('entrada segundaria grupo 2 izquierda', 'Entrada segundaria grupo 2 izquierda'), ('entrada segundaria grupo 2 derecha', 'Entrada segundaria grupo 2 derecha'), ('entrada segundaria grupo 3 izquierda', 'Entrada segundaria grupo 3 izquierda'), ('entrada segundaria grupo 3 derecha', 'Entrada segundaria grupo 3 derecha'), ('entrada segundaria grupo 4 izquierda', 'Entrada segundaria grupo 4 izquierda'), ('entrada segundaria grupo 4 derecha', 'Entrada segundaria grupo 4 derecha'), ('entrada grupo 1 larga', 'Entrada grupo 1 larga'), ('entrada grupo 2 larga', 'Entrada grupo 2 larga')], help_text='Escoja el tipo', max_length=36, null=True)),
            ],
            options={
                'verbose_name': 'Local',
                'verbose_name_plural': 'Locales',
            },
        ),
        migrations.CreateModel(
            name='Metraje',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('area', models.CharField(help_text="Área total en metros cuadrados (ejemplo: '12.5 m²')", max_length=50)),
                ('altura', models.CharField(help_text="Altura en metros (ejemplo: '4.5 m')", max_length=50)),
                ('perimetro', models.CharField(help_text="Perímetro en metros (ejemplo: '2.5 x 5')", max_length=50)),
                ('image', models.ImageField(blank=True, help_text='Cargar una imagen para el metraje', null=True, upload_to='metraje_images/')),
            ],
        ),
        migrations.CreateModel(
            name='PrecioBase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('precio', models.DecimalField(decimal_places=2, help_text='Coloca el monto del local', max_digits=10)),
            ],
            options={
                'verbose_name': 'Precio Base',
                'verbose_name_plural': 'Precios Base',
            },
        ),
        migrations.CreateModel(
            name='TipoVenta',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tipo', models.CharField(choices=[('credito', 'Crédito'), ('contado', 'Contado')], help_text='Tipo de venta: crédito o contado', max_length=10, unique=True)),
                ('descripcion', models.TextField(blank=True, help_text='Descripción del tipo de venta', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Zona',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('codigo', models.CharField(help_text='Código único de 10 dígitos para la zona', max_length=10, unique=True)),
                ('linea_base', models.CharField(choices=[('primera_linea', 'Primera Línea'), ('segunda_linea', 'Segunda Línea'), ('tercera_linea', 'Tercera Línea')], default='primera_linea', help_text='Línea base de la zona', max_length=15)),
                ('tiene_subniveles', models.BooleanField(default=False)),
                ('categoria', models.ForeignKey(help_text='Categoría asociada a esta zona', on_delete=django.db.models.deletion.CASCADE, related_name='zonas', to='locales.categoria')),
            ],
        ),
        migrations.CreateModel(
            name='VentaCredito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicial', models.DecimalField(decimal_places=2, help_text='Monto inicial a pagar', max_digits=10)),
                ('cuotas', models.PositiveIntegerField(help_text='Número de cuotas')),
                ('monto_por_mes', models.DecimalField(decimal_places=2, help_text='Monto a pagar por mes', max_digits=10)),
                ('tipo_venta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='venta_credito', to='locales.tipoventa')),
            ],
        ),
        migrations.CreateModel(
            name='VentaContado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicial', models.DecimalField(decimal_places=2, help_text='Monto inicial a pagar', max_digits=10)),
                ('descuento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ventas_contado', to='locales.descuento')),
                ('tipo_venta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='venta_contado', to='locales.tipoventa')),
            ],
        ),
        migrations.CreateModel(
            name='TipoDescuento',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('condiciones', models.TextField(blank=True, null=True)),
                ('categoria', models.ForeignKey(help_text='Categoría asociada al tipo de descuento', on_delete=django.db.models.deletion.CASCADE, related_name='tipo_descuentos', to='locales.categoria')),
            ],
        ),
        migrations.CreateModel(
            name='ReciboArras',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('serie', models.CharField(help_text='Serie única del recibo de arras', max_length=20, unique=True)),
                ('fecha_creacion', models.DateField(auto_now_add=True, help_text='Fecha de creación del recibo')),
                ('fecha_vencimiento', models.DateField(help_text='Fecha de vencimiento del recibo')),
                ('nombre_cliente', models.CharField(help_text='Nombre completo del cliente', max_length=255)),
                ('dni_cliente', models.CharField(help_text='DNI del cliente', max_length=15)),
                ('nombre_conyugue', models.CharField(blank=True, help_text='Nombre completo del cónyuge', max_length=255, null=True)),
                ('dni_conyugue', models.CharField(blank=True, help_text='DNI del cónyuge', max_length=15, null=True)),
                ('nombre_copropietario', models.CharField(blank=True, help_text='Nombre completo del copropietario', max_length=255, null=True)),
                ('dni_copropietario', models.CharField(blank=True, help_text='DNI del copropietario', max_length=15, null=True)),
                ('razon_social', models.CharField(blank=True, help_text='Razón social del cliente', max_length=255, null=True)),
                ('ruc', models.CharField(blank=True, help_text='RUC del cliente', max_length=20, null=True)),
                ('direccion', models.CharField(help_text='Dirección del cliente', max_length=255)),
                ('correo', models.EmailField(help_text='Correo electrónico del cliente', max_length=254)),
                ('celular', models.CharField(help_text='Número de celular del cliente', max_length=20)),
                ('nro_operacion', models.CharField(blank=True, help_text='Número de operación bancaria', max_length=50, null=True)),
                ('metodo_separacion', models.CharField(choices=[('efectivo', 'Efectivo'), ('deposito', 'Depósito'), ('banco', 'Banco')], default='efectivo', help_text='Método de separación', max_length=10)),
                ('precio_lista', models.DecimalField(blank=True, decimal_places=2, help_text='Precio lista del local', max_digits=10, null=True)),
                ('condicion', models.CharField(blank=True, help_text='Condición asociada al local', max_length=100, null=True)),
                ('monto_separacion', models.DecimalField(decimal_places=2, help_text='Monto de separación en soles o dólares', max_digits=10)),
                ('moneda', models.CharField(choices=[('PEN', 'Soles'), ('USD', 'Dólares')], default='PEN', help_text='Moneda del monto de separación', max_length=3)),
                ('local', models.ForeignKey(help_text='Local asociado al recibo', on_delete=django.db.models.deletion.PROTECT, to='locales.local')),
                ('zona', models.ForeignKey(blank=True, help_text='Zona asociada al local (rellenado automáticamente)', null=True, on_delete=django.db.models.deletion.PROTECT, to='locales.zona')),
            ],
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto_separacion', models.DecimalField(decimal_places=2, help_text='Monto de separación aplicado', max_digits=10)),
                ('recibo_arras', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='locales.reciboarras')),
                ('tipo_venta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pagos', to='locales.tipoventa')),
            ],
        ),
        migrations.AddField(
            model_name='local',
            name='metraje',
            field=models.ForeignKey(help_text='Metraje asociado al local.', on_delete=django.db.models.deletion.CASCADE, related_name='locales', to='locales.metraje'),
        ),
        migrations.AddField(
            model_name='local',
            name='precio_base',
            field=models.ForeignKey(blank=True, help_text='Precio base asociado al local.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='locales', to='locales.preciobase'),
        ),
        migrations.AddField(
            model_name='local',
            name='subnivel_de',
            field=models.ForeignKey(blank=True, help_text='Local principal que permite subniveles.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subniveles', to='locales.local'),
        ),
        migrations.AddField(
            model_name='local',
            name='zona',
            field=models.ForeignKey(help_text='Zona a la que pertenece este local.', on_delete=django.db.models.deletion.CASCADE, related_name='locales', to='locales.zona'),
        ),
        migrations.AddField(
            model_name='descuento',
            name='metraje',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descuentos', to='locales.metraje'),
        ),
        migrations.AddField(
            model_name='descuento',
            name='tipo_descuento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='descuentos', to='locales.tipodescuento'),
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_cliente', models.CharField(help_text='Nombre completo del cliente', max_length=255)),
                ('dni_cliente', models.CharField(help_text='DNI del cliente (8 dígitos)', max_length=8)),
                ('direccion_cliente', models.CharField(help_text='Dirección del cliente', max_length=255)),
                ('ruc', models.CharField(blank=True, help_text='RUC del cliente', max_length=20, null=True)),
                ('correo', models.EmailField(help_text='Correo electrónico del cliente', max_length=254)),
                ('f_nacimiento_cliente', models.DateField(blank=True, help_text='Fecha de nacimiento del cliente', null=True)),
                ('ocupacion_cliente', models.CharField(blank=True, help_text='Ocupación del cliente', max_length=100, null=True)),
                ('telefono_cliente', models.CharField(help_text='Teléfono del cliente', max_length=20)),
                ('nombre_copropietario', models.CharField(blank=True, help_text='Nombre completo del copropietario', max_length=255, null=True)),
                ('dni_copropietario', models.CharField(blank=True, help_text='DNI del copropietario (8 dígitos)', max_length=8, null=True)),
                ('direccion_copropietario', models.CharField(blank=True, help_text='Dirección del copropietario', max_length=255, null=True)),
                ('f_nacimiento_copropietario', models.DateField(blank=True, help_text='Fecha de nacimiento del copropietario', null=True)),
                ('ocupacion_copropietario', models.CharField(blank=True, help_text='Ocupación del copropietario', max_length=100, null=True)),
                ('telefono_copropietario', models.CharField(blank=True, help_text='Teléfono del copropietario', max_length=20, null=True)),
                ('parentesco', models.CharField(blank=True, help_text='Parentesco con el cliente', max_length=50, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, help_text='Fecha de creación del registro')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, help_text='Fecha de última actualización del registro')),
                ('local', models.ForeignKey(help_text='Local asociado al cliente', on_delete=django.db.models.deletion.CASCADE, related_name='clientes', to='locales.local')),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
            },
        ),
        migrations.AlterUniqueTogether(
            name='descuento',
            unique_together={('categoria', 'metraje', 'tipo_descuento')},
        ),
    ]
