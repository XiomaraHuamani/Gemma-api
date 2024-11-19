from rest_framework import serializers
from .models import Zona, Metraje, TipoDescuento, PrecioBase, Descuento, Local, ReciboArras, Cliente


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
    class Meta:
        model = ReciboArras
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
