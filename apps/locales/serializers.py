from rest_framework import serializers
from .models import Zona, Metraje, TipoDescuento, PrecioBase, Descuento, Local, ReciboArras, Cliente, Pago, VentaContado, VentaCredito, Categoria
from decimal import Decimal


class ZonaSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Zona
        fields = ['id', 'categoria', 'categoria_nombre', 'codigo', 'linea_base']

    def get_display_name(self, obj):
        return f"{obj.nombre} - Código: {obj.codigo} - Línea: {obj.get_linea_base_display()}"
    

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']


class MetrajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metraje
        fields = '__all__'


class TipoDescuentoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = TipoDescuento
        fields = ['id', 'nombre', 'descripcion', 'condiciones', 'categoria', 'categoria_nombre']

class PrecioBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecioBase
        fields = '__all__'


class DescuentoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    tipo_descuento = serializers.PrimaryKeyRelatedField(
        queryset=TipoDescuento.objects.none()  # Inicialmente vacío
    )

    class Meta:
        model = Descuento
        fields = ['id', 'categoria', 'categoria_nombre', 'tipo_descuento', 'metraje', 'monto', 'porcentaje']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'categoria' in self.initial_data:
            try:
                categoria_id = self.initial_data['categoria']
                self.fields['tipo_descuento'].queryset = TipoDescuento.objects.filter(categoria_id=categoria_id)
            except ValueError:
                pass


class LocalSerializer(serializers.ModelSerializer):
    zona_nombre = serializers.CharField(source='zona.nombre', read_only=True)
    metraje_area = serializers.CharField(source='metraje.area', read_only=True)

    class Meta:
        model = Local
        fields = ['id', 'zona', 'zona_nombre', 'metraje', 'metraje_area', 'estado', 'precio']


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


