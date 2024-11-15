from rest_framework import serializers
from .models import Zona, Metraje, PrecioBase, Descuento, Local, ReciboArras, Cliente

class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = ['id', 'nombre', 'codigo']


class MetrajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metraje
        fields = ['id', 'area', 'altura', 'perimetro']


class PrecioBaseSerializer(serializers.ModelSerializer):
    zona = ZonaSerializer()
    metraje = MetrajeSerializer()

    class Meta:
        model = PrecioBase
        fields = ['id', 'zona', 'metraje', 'precio']


class DescuentoSerializer(serializers.ModelSerializer):
    zona = ZonaSerializer()
    metraje = MetrajeSerializer()
    monto_descuento = serializers.SerializerMethodField()

    class Meta:
        model = Descuento
        fields = ['id', 'zona', 'metraje', 'porcentaje', 'monto_descuento']

    def get_monto_descuento(self, obj):
        return obj.calcular_monto_descuento()


class LocalSerializer(serializers.ModelSerializer):
    zona = ZonaSerializer()
    metraje = MetrajeSerializer()
    precio_base = serializers.SerializerMethodField()
    descuento = serializers.SerializerMethodField()
    precio_final = serializers.SerializerMethodField()

    class Meta:
        model = Local
        fields = ['id', 'zona', 'metraje', 'estado', 'precio_base', 'descuento', 'precio_final']

    def get_precio_base(self, obj):
        return obj.obtener_precio_base()

    def get_descuento(self, obj):
        return obj.obtener_descuento()

    def get_precio_final(self, obj):
        return obj.calcular_precio_final()


class ReciboArrasSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    zona = ZonaSerializer()
    local = LocalSerializer()
    metraje = MetrajeSerializer()

    class Meta:
        model = ReciboArras
        fields = [
            'id', 'numero', 'fecha', 'fecha_vencimiento', 'cliente', 'direccion', 'email', 'telefono',
            'monto_efectivo', 'monto_deposito', 'banco', 'numero_operacion_bancaria', 'proyecto',
            'zona', 'local', 'metraje', 'precio_lista', 'precio_final', 'condicion', 'plazo'
        ]


class ClienteSerializer(serializers.ModelSerializer):
    local = LocalSerializer()

    class Meta:
        model = Cliente
        fields = [
            'id_cliente', 'local', 'nombre_proyecto', 'usuario_credencial', 'razon_social',
            'nombres', 'apellido_paterno', 'apellido_materno', 'dni', 'direccion', 'numero_cel',
            'correo', 'fecha_creacion', 'fecha_actualizacion'
        ]
