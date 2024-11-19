from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum


class Zona(models.Model):
    LINEA_BASE_CHOICES = [
        ('primera_linea', 'Primera Línea'),
        ('segunda_linea', 'Segunda Línea'),
        ('tercera_linea', 'Tercera Línea'),
    ]

    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=10, unique=True, help_text="Código único de 10 dígitos para la zona")
    linea_base = models.CharField(
        max_length=15,
        choices=LINEA_BASE_CHOICES,
        default='primera_linea',
        help_text="Línea base de la zona"
    )

    def __str__(self):
        return f"{self.nombre} - Código: {self.codigo} - Línea: {self.get_linea_base_display()}"
    
    def clean(self):
        if not self.codigo.isupper():
            raise ValidationError("El código de la zona debe estar en mayúsculas.")



class Metraje(models.Model):
    id = models.AutoField(primary_key=True)
    area = models.CharField(max_length=50, help_text="Área total en metros cuadrados (ejemplo: '12.5 m²')")
    altura = models.CharField(max_length=50, help_text="Altura en metros (ejemplo: '4.5 m')")
    perimetro = models.CharField(max_length=50, help_text="Perímetro en metros (ejemplo: '2.5 x 5')")
    image = models.ImageField(upload_to='metraje_images/', blank=True, null=True, help_text="Cargar una imagen para el metraje")

    def __str__(self):
        return f"Área: {self.area} - Altura: {self.altura} - Perímetro: {self.perimetro}"


class TipoDescuento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    condiciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class PrecioBase(models.Model):
    id = models.AutoField(primary_key=True)
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE, related_name='precios_base')
    metraje = models.ForeignKey(Metraje, on_delete=models.CASCADE, related_name='precios_base')
    precio = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio base para la combinación de zona y metraje")

    class Meta:
        unique_together = ('zona', 'metraje')
        verbose_name = "Precio Base"
        verbose_name_plural = "Precios Base"

    def __str__(self):
        return f"Precio base en {self.zona} para {self.metraje}: {self.precio}"


class Descuento(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_descuento = models.ForeignKey(TipoDescuento, on_delete=models.CASCADE, related_name='descuentos')
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE, related_name='descuentos')
    metraje = models.ForeignKey(Metraje, on_delete=models.CASCADE, related_name='descuentos')
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Monto de descuento opcional")
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Porcentaje de descuento opcional")

    class Meta:
        unique_together = ('zona', 'metraje', 'tipo_descuento')
        verbose_name = "Descuento"
        verbose_name_plural = "Descuentos"

    def clean(self):
        if self.monto and self.porcentaje:
            raise ValidationError("Debe especificar solo uno: monto o porcentaje.")
        if not self.monto and not self.porcentaje:
            raise ValidationError("Debe especificar al menos un monto o porcentaje para el descuento.")


    def calcular_monto_descuento(self):
        try:
            precio_base = PrecioBase.objects.get(zona=self.zona, metraje=self.metraje)
            if self.porcentaje:
                return precio_base.precio * (self.porcentaje / 100)
            return self.monto or 0
        except PrecioBase.DoesNotExist:
            return 0

    def __str__(self):
        return f"Descuento {self.tipo_descuento} en {self.zona} para {self.metraje}"


class Local(models.Model):
    id = models.AutoField(primary_key=True)
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE, related_name='locales')
    metraje = models.ForeignKey(Metraje, on_delete=models.CASCADE, help_text="Rango de metraje del local")
    estado = models.CharField(
        max_length=10,
        choices=[('disponible', 'Disponible'), ('separado', 'Separado'), ('vendido', 'Vendido')],
        default='disponible'
    )

    def obtener_precio_base(self):
        try:
            return PrecioBase.objects.get(zona=self.zona, metraje=self.metraje).precio
        except PrecioBase.DoesNotExist:
            return None

    def obtener_descuento(self):
        # Optimización con agregación
        return Descuento.objects.filter(zona=self.zona, metraje=self.metraje).aggregate(
            total_descuento=Sum('monto')
        )['total_descuento'] or 0

    def calcular_precio_final(self):
        precio_base = self.obtener_precio_base() or 0
        descuento = self.obtener_descuento()
        return precio_base - descuento

    def __str__(self):
        return f"Local {self.id} - {self.zona.nombre} - {self.metraje.area} - Estado: {self.estado}"


class ReciboArras(models.Model):
    id = models.AutoField(primary_key=True)  # Clave primaria auto incremental
    numero = models.CharField(max_length=20, unique=True)
    fecha = models.DateField()
    fecha_vencimiento = models.DateField()
    cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT)
    direccion = models.CharField(max_length=255)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    monto_efectivo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    monto_deposito = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    banco = models.CharField(max_length=50, blank=True, null=True)
    numero_operacion_bancaria = models.CharField(max_length=50, blank=True, null=True)
    proyecto = models.CharField(max_length=100)
    zona = models.ForeignKey('Zona', on_delete=models.PROTECT)
    local = models.ForeignKey('Local', on_delete=models.PROTECT)
    metraje = models.ForeignKey('Metraje', on_delete=models.PROTECT)
    precio_lista = models.DecimalField(max_digits=10, decimal_places=2)
    precio_final = models.DecimalField(max_digits=10, decimal_places=2)
    condicion = models.CharField(max_length=100)
    plazo = models.CharField(max_length=100)

    def clean(self):
        """
        Validación para asegurarse de que el precio final coincide con el precio calculado
        basado en el descuento aplicado al local.
        """
        precio_calculado = self.local.calcular_precio_final()
        if self.precio_final != precio_calculado:
            raise ValidationError(f"El precio final debe ser {precio_calculado} basado en el descuento aplicado.")

    def __str__(self):
        return f"Recibo de arras #{self.numero} - Cliente: {self.cliente.nombres}"


class Cliente(models.Model):
    id = models.AutoField(primary_key=True)  # Clave primaria auto incremental
    local = models.ForeignKey('Local', on_delete=models.CASCADE, related_name='clientes')
    nombre_proyecto = models.CharField(max_length=100, help_text="Nombre del proyecto al que está asociado el cliente")
    usuario_credencial = models.CharField(max_length=50, help_text="Nombre de usuario o credencial")
    razon_social = models.CharField(max_length=255, blank=True, null=True, help_text="Razón social del cliente si aplica")
    nombres = models.CharField(max_length=100, help_text="Nombres del cliente")
    apellido_paterno = models.CharField(max_length=100, help_text="Apellido paterno del cliente")
    apellido_materno = models.CharField(max_length=100, help_text="Apellido materno del cliente")
    dni = models.IntegerField(help_text="Documento de identidad del cliente")
    direccion = models.CharField(max_length=255, help_text="Dirección del cliente")
    numero_cel = models.IntegerField(help_text="Número de celular del cliente")
    correo = models.EmailField(help_text="Correo electrónico del cliente")
    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación del registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, help_text="Fecha de última actualización del registro")

    def __str__(self):
        return f"{self.nombres} {self.apellido_paterno} ({self.dni})"
