from rest_framework import serializers
from .models import Zona, Metraje, TipoDescuento, PrecioBase, Descuento, Local, ReciboArras, Cliente, Pago, VentaContado, VentaCredito
from decimal import Decimal


class ZonaSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Zona
        fields = ['id', 'codigo', 'nombre', 'linea_base', 'display_name']

    def get_display_name(self, obj):
        return f"{obj.nombre} - Código: {obj.codigo} - Línea: {obj.get_linea_base_display()}"


class MetrajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metraje
        fields = '__all__'


class TipoDescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDescuento
        fields = '__all__'


class PrecioBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecioBase
        fields = '__all__'


class DescuentoSerializer(serializers.ModelSerializer):
    zona = serializers.PrimaryKeyRelatedField(
        queryset=Zona.objects.all(),
        write_only=True
    )
    zona_detail = ZonaSerializer(source='zona', read_only=True)

    class Meta:
        model = Descuento
        fields = '__all__'


class LocalSerializer(serializers.ModelSerializer):
    precio_base = serializers.SerializerMethodField()
    descuento = serializers.SerializerMethodField()
    precio_final = serializers.SerializerMethodField()

    class Meta:
        model = Local
        fields = '__all__'

    def get_precio_base(self, obj):
        return obj.obtener_precio_base()

    def get_descuento(self, obj):
        return obj.obtener_descuento()

    def get_precio_final(self, obj):
        return obj.calcular_precio_final()


class ReciboArrasSerializer(serializers.ModelSerializer):
    zona = serializers.StringRelatedField(read_only=True)  # Zona será solo de lectura, derivada del local
    precio_lista = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # Solo lectura
    condicion = serializers.CharField(read_only=True)  # Solo lectura
    local_codigo = serializers.CharField(source="local.codigo", read_only=True)  # Muestra el código del local

    class Meta:
        model = ReciboArras
        fields = [
            'id',
            'serie',
            'fecha_creacion',
            'fecha_vencimiento',
            'nombre_cliente',
            'dni_cliente',
            'nombre_conyugue',
            'dni_conyugue',
            'nombre_copropietario',
            'dni_copropietario',
            'razon_social',
            'ruc',
            'direccion',
            'correo',
            'celular',
            'nro_operacion',
            'metodo_separacion',
            'local',
            'local_codigo',
            'zona',
            'precio_lista',
            'condicion',
            'monto_separacion',
            'moneda',
        ]

    def validate(self, data):
        """
        Validación personalizada del monto de separación.
        """
        if data['moneda'] == 'USD' and data['monto_separacion'] < Decimal('900.00'):
            raise serializers.ValidationError("El monto de separación en dólares debe ser al menos 900 USD.")
        return data


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

    def validate_dni_cliente(self, value):
        """
        Validación personalizada para el DNI del cliente.
        """
        if len(value) != 8:
            raise serializers.ValidationError("El DNI del cliente debe tener exactamente 8 dígitos.")
        return value

    def validate_dni_copropietario(self, value):
        """
        Validación personalizada para el DNI del copropietario.
        """
        if value and len(value) != 8:
            raise serializers.ValidationError("El DNI del copropietario debe tener exactamente 8 dígitos.")
        return value
    
class VentaCreditoSerializer(serializers.ModelSerializer):
    total_a_pagar = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = VentaCredito
        fields = ['tipo_venta', 'inicial', 'cuotas', 'monto_por_mes', 'total_a_pagar']


class VentaContadoSerializer(serializers.ModelSerializer):
    total_a_pagar = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = VentaContado
        fields = ['tipo_venta', 'inicial', 'descuento', 'total_a_pagar']


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['recibo_arras', 'tipo_venta', 'monto_separacion']


