from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from decimal import Decimal


class Zona(models.Model):
    LINEA_BASE_CHOICES = [
        ('primera_linea', 'Primera Línea'),
        ('segunda_linea', 'Segunda Línea'),
        ('tercera_linea', 'Tercera Línea'),
    ]

    id = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(
        'Categoria',
        on_delete=models.CASCADE,
        related_name='zonas',
        help_text="Categoría asociada a esta zona"
    )
    codigo = models.CharField(max_length=10, unique=True, help_text="Código único de 10 dígitos para la zona")
    linea_base = models.CharField(
        max_length=15,
        choices=LINEA_BASE_CHOICES,
        default='primera_linea',
        help_text="Línea base de la zona"
    )
    tiene_subniveles = models.BooleanField(
        default=False,
        help_text="Indica si la zona tiene subniveles asociados"
    )

    def __str__(self):
        return f"{self.categoria.nombre} - Código: {self.codigo}"


class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre único para la categoría de zona")

    def __str__(self):
        return self.nombre



class Metraje(models.Model):
    id = models.AutoField(primary_key=True)
    area = models.CharField(max_length=50, help_text="Área total en metros cuadrados (ejemplo: '12.5 m²')")
    altura = models.CharField(max_length=50, help_text="Altura en metros (ejemplo: '4.5 m')")
    perimetro = models.CharField(max_length=50, help_text="Perímetro en metros (ejemplo: '2.5 x 5')")
    image = models.ImageField(
        upload_to='metraje_images/',
        blank=True,
        null=True,
        help_text="Cargar una imagen para el metraje"
    )

    def __str__(self):
        return f"Área: {self.area} - Altura: {self.altura} - Perímetro: {self.perimetro}"



class TipoDescuento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    condiciones = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(
        'Categoria',
        on_delete=models.CASCADE,
        related_name='tipo_descuentos',  
        help_text="Categoría asociada al tipo de descuento"
    )

    def __str__(self):
        return f"{self.nombre} - {self.categoria.nombre}"


class PrecioBase(models.Model):
    id = models.AutoField(primary_key=True)
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Coloca el monto del local"
    )

    class Meta:
        verbose_name = "Precio Base"
        verbose_name_plural = "Precios Base"

    def __str__(self):
        return f"ID: {self.id} - Precio: {self.precio}"



class Descuento(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_descuento = models.ForeignKey(
        TipoDescuento,
        on_delete=models.PROTECT,  
        related_name='descuentos'
    )
    categoria = models.ForeignKey(
        'Categoria',
        on_delete=models.PROTECT,  # Evita eliminar categorías con descuentos asociados
        related_name='descuentos',
        help_text="Categoría asociada al descuento"
    )
    metraje = models.ForeignKey(
        Metraje,
        on_delete=models.CASCADE,
        related_name='descuentos'
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Monto de descuento opcional"
    )
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Porcentaje de descuento opcional"
    )

    class Meta:
        unique_together = ('categoria', 'metraje', 'tipo_descuento')  # Asegura unicidad
        verbose_name = "Descuento"
        verbose_name_plural = "Descuentos"

    def clean(self):
        """
        Validaciones personalizadas.
        """
        if self.monto and self.porcentaje:
            raise ValidationError("Solo puede especificar un monto o un porcentaje, no ambos.")
        if not self.monto and not self.porcentaje:
            raise ValidationError("Debe especificar al menos un monto o un porcentaje para el descuento.")

    @property
    def descuento_aplicado(self):
        """
        Calcula el descuento basado en el monto o porcentaje.
        """
        if self.monto:
            return self.monto
        if self.porcentaje:
            precio_base = PrecioBase.objects.filter(metraje=self.metraje, zona=self.categoria).first()
            if precio_base:
                return precio_base.precio * (self.porcentaje / 100)
        return 0

    def __str__(self):
        return f"{self.categoria.nombre} - {self.tipo_descuento.nombre} - {self.metraje.area}"


class Local(models.Model):
    zona = models.ForeignKey(
        'Zona',
        on_delete=models.CASCADE,
        related_name='locales',
        help_text="Zona a la que pertenece este local."
    )
    metraje = models.ForeignKey(
        'Metraje',
        on_delete=models.CASCADE,
        related_name='locales',
        help_text="Metraje asociado al local."
    )
    estado = models.CharField(
        max_length=20,
        choices=[('disponible', 'Disponible'), ('reservado', 'Reservado'), ('vendido', 'Vendido')],
        default='disponible',
        help_text="Estado del local (disponible, reservado, vendido)."
    )
    precio_base = models.ForeignKey(
        'PrecioBase',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locales',
        help_text="Precio base asociado al local."
    )
    tipo = models.CharField( 
        max_length=36,
        choices=[
            ("entrada segundaria grupo 1 izquierda", "Entrada secundaria grupo 1 izquierda"),
            ("entrada segundaria grupo 1 derecha", "Entrada secundaria grupo 1 derecha"),
            ("entrada segundaria grupo 2 izquierda", "Entrada secundaria grupo 2 izquierda"),
            ("entrada segundaria grupo 2 derecha", "Entrada secundaria grupo 2 derecha"),
            ("entrada segundaria grupo 3 izquierda", "Entrada secundaria grupo 3 izquierda"),
            ("entrada segundaria grupo 3 derecha", "Entrada secundaria grupo 3 derecha"),
            ("entrada segundaria grupo 4 izquierda", "Entrada secundaria grupo 4 izquierda"),
            ("entrada segundaria grupo 4 derecha", "Entrada secundaria grupo 4 derecha"),
            ("entrada grupo 1 larga", "Entrada grupo 1 larga"),
            ("entrada grupo 2 larga", "Entrada grupo 2 larga"),
        ],
        null=True,
        blank=True,
        help_text="Escoja el tipo"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['zona', 'metraje'], name='unique_local_per_zona_metraje')
        ]
        verbose_name = "Local"
        verbose_name_plural = "Locales"

    def __str__(self):
        return f"Local - Zona: {self.zona.codigo} - Metraje: {self.metraje.area}"


class ReciboArras(models.Model):
    id = models.AutoField(primary_key=True)  # Clave primaria auto incremental
    serie = models.CharField(max_length=20, unique=True, help_text="Serie única del recibo de arras")
    fecha_creacion = models.DateField(auto_now_add=True, help_text="Fecha de creación del recibo")
    fecha_vencimiento = models.DateField(help_text="Fecha de vencimiento del recibo")

    # Información del cliente
    nombre_cliente = models.CharField(max_length=255, help_text="Nombre completo del cliente")
    dni_cliente = models.CharField(max_length=15, help_text="DNI del cliente")
    nombre_conyugue = models.CharField(max_length=255, blank=True, null=True, help_text="Nombre completo del cónyuge")
    dni_conyugue = models.CharField(max_length=15, blank=True, null=True, help_text="DNI del cónyuge")
    nombre_copropietario = models.CharField(max_length=255, blank=True, null=True, help_text="Nombre completo del copropietario")
    dni_copropietario = models.CharField(max_length=15, blank=True, null=True, help_text="DNI del copropietario")
    razon_social = models.CharField(max_length=255, blank=True, null=True, help_text="Razón social del cliente")
    ruc = models.CharField(max_length=20, blank=True, null=True, help_text="RUC del cliente")
    direccion = models.CharField(max_length=255, help_text="Dirección del cliente")
    correo = models.EmailField(help_text="Correo electrónico del cliente")
    celular = models.CharField(max_length=20, help_text="Número de celular del cliente")

    # Información de operación
    nro_operacion = models.CharField(max_length=50, blank=True, null=True, help_text="Número de operación bancaria")
    metodo_separacion = models.CharField(
        max_length=10,
        choices=[
            ('efectivo', 'Efectivo'),
            ('deposito', 'Depósito'),
            ('banco', 'Banco')
        ],
        default='efectivo',
        help_text="Método de separación"
    )

    # Información relacionada al local
    local = models.ForeignKey('Local', on_delete=models.PROTECT, help_text="Local asociado al recibo")
    zona = models.ForeignKey('Zona', on_delete=models.PROTECT, blank=True, null=True, help_text="Zona asociada al local (rellenado automáticamente)")
    precio_lista = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Precio lista del local")
    condicion = models.CharField(max_length=100, blank=True, null=True, help_text="Condición asociada al local")

    # Montos de separación
    monto_separacion = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monto de separación en soles o dólares")
    moneda = models.CharField(
        max_length=3,
        choices=[
            ('PEN', 'Soles'),
            ('USD', 'Dólares')
        ],
        default='PEN',
        help_text="Moneda del monto de separación"
    )

    def validate_monto_separacion(self):
        if self.moneda == 'USD' and self.monto_separacion < Decimal('900.00'):
            raise ValidationError("El monto de separación en dólares debe ser al menos 900 USD.")

    def autofill_fields(self):
        """
        Rellena automáticamente campos relacionados al local.
        """
        if self.local:
            self.zona = self.local.zona
            self.precio_lista = self.local.obtener_precio_base() or 0
            self.condicion = "Separación"

    def clean(self):
        self.validate_monto_separacion()
        self.autofill_fields()


class Cliente(models.Model):
    id = models.AutoField(primary_key=True)

    # Relación con Local
    local = models.ForeignKey(
        'Local',
        on_delete=models.CASCADE,
        related_name='clientes',
        help_text="Local asociado al cliente"
    )

    # Datos del Cliente
    nombre_cliente = models.CharField(max_length=255, help_text="Nombre completo del cliente")
    dni_cliente = models.CharField(max_length=8, help_text="DNI del cliente (8 dígitos)")
    direccion_cliente = models.CharField(max_length=255, help_text="Dirección del cliente")
    ruc = models.CharField(max_length=20, blank=True, null=True, help_text="RUC del cliente")
    correo = models.EmailField(help_text="Correo electrónico del cliente")
    f_nacimiento_cliente = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha de nacimiento del cliente"
    )
    ocupacion_cliente = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Ocupación del cliente"
    )
    telefono_cliente = models.CharField(max_length=20, help_text="Teléfono del cliente")

    # Datos del Copropietario
    nombre_copropietario = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nombre completo del copropietario"
    )
    dni_copropietario = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        help_text="DNI del copropietario (8 dígitos)"
    )
    direccion_copropietario = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Dirección del copropietario"
    )
    f_nacimiento_copropietario = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha de nacimiento del copropietario"
    )
    ocupacion_copropietario = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Ocupación del copropietario"
    )
    telefono_copropietario = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Teléfono del copropietario"
    )
    parentesco = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Parentesco con el cliente"
    )

    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación del registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, help_text="Fecha de última actualización del registro")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.nombre_cliente} ({self.dni_cliente})"

    def validate_dni(self):
        if len(self.dni_cliente) != 8:
            raise ValidationError("El DNI del cliente debe tener exactamente 8 dígitos.")
        if self.dni_copropietario and len(self.dni_copropietario) != 8:
            raise ValidationError("El DNI del copropietario debe tener exactamente 8 dígitos.")

    def autofill_from_existing(self):
        cliente_existente = Cliente.objects.filter(dni_cliente=self.dni_cliente).first()
        if cliente_existente:
            # Copia los datos existentes
            self.nombre_cliente = cliente_existente.nombre_cliente
            self.direccion_cliente = cliente_existente.direccion_cliente
            self.ruc = cliente_existente.ruc
            self.correo = cliente_existente.correo
            self.f_nacimiento_cliente = cliente_existente.f_nacimiento_cliente
            self.ocupacion_cliente = cliente_existente.ocupacion_cliente
            self.telefono_cliente = cliente_existente.telefono_cliente

        def clean(self):
            self.validate_dni()

        def save(self, *args, **kwargs):
            self.autofill_from_existing()
            super().save(*args, **kwargs)


class TipoVenta(models.Model):
    TIPO_CHOICES = [
        ('credito', 'Crédito'),
        ('contado', 'Contado'),
    ]

    id = models.AutoField(primary_key=True)
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        unique=True,
        help_text="Tipo de venta: crédito o contado"
    )
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción del tipo de venta")

    def __str__(self):
        return self.tipo


class VentaCredito(models.Model):
    tipo_venta = models.OneToOneField(TipoVenta, on_delete=models.CASCADE, related_name='venta_credito')
    inicial = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monto inicial a pagar")
    cuotas = models.PositiveIntegerField(help_text="Número de cuotas")
    monto_por_mes = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monto a pagar por mes")

    def total_a_pagar(self):
        return self.inicial + (self.cuotas * self.monto_por_mes)

    def __str__(self):
        return f"Crédito: Inicial {self.inicial}, {self.cuotas} cuotas de {self.monto_por_mes}"


class VentaContado(models.Model):
    tipo_venta = models.OneToOneField(TipoVenta, on_delete=models.CASCADE, related_name='venta_contado')
    inicial = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monto inicial a pagar")
    descuento = models.ForeignKey('Descuento', on_delete=models.CASCADE, related_name='ventas_contado')

    def calcular_descuento(self):
        if self.descuento.porcentaje:
            return self.inicial * (self.descuento.porcentaje / 100)
        return self.descuento.monto or 0

    def total_a_pagar(self):
        descuento_aplicado = self.calcular_descuento()
        return max(self.inicial - descuento_aplicado, Decimal('0.00'))

    def __str__(self):
        return f"Contado: Inicial {self.inicial}, descuento {self.descuento}"


class Pago(models.Model):
    recibo_arras = models.ForeignKey('ReciboArras', on_delete=models.CASCADE, related_name='pagos')
    tipo_venta = models.ForeignKey(TipoVenta, on_delete=models.PROTECT, related_name='pagos')
    monto_separacion = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monto de separación aplicado")

    def aplicar_monto_separacion(self):
        """
        Resta el monto de separación de la inicial.
        """
        if hasattr(self.tipo_venta, 'venta_credito'):
            venta_credito = self.tipo_venta.venta_credito
            venta_credito.inicial -= self.monto_separacion
            venta_credito.save()
        elif hasattr(self.tipo_venta, 'venta_contado'):
            venta_contado = self.tipo_venta.venta_contado
            venta_contado.inicial -= self.monto_separacion
            venta_contado.save()

    def save(self, *args, **kwargs):
        self.aplicar_monto_separacion()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Pago relacionado al recibo {self.recibo_arras.serie}"
