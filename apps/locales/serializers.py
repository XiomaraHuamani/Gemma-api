from rest_framework import serializers, status
from rest_framework.response import Response
from .models import Zona, Metraje, TipoDescuento, PrecioBase, Descuento, Local, ReciboArras, Cliente, Pago, VentaContado, VentaCredito, Categoria 
from decimal import Decimal
from rest_framework.exceptions import ValidationError


class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = ['id', 'categoria', 'codigo', 'linea_base']
        extra_kwargs = {
            'codigo': {'required': True},
        }

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
        fields = ['id', 'precio']

class DescuentoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    tipo_descuento_nombre = serializers.CharField(source='tipo_descuento.nombre', read_only=True)
    descuento_aplicado = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Descuento
        fields = ['id', 'categoria', 'categoria_nombre', 'tipo_descuento', 'tipo_descuento_nombre', 
                'metraje', 'monto', 'porcentaje', 'descuento_aplicado']

class SimpleLocalSerializer(serializers.ModelSerializer):
    """
    Serializer que retorna solo los campos planos sin estructura anidada.
    """
    image = serializers.SerializerMethodField()

    class Meta:
        model = Local
        fields = [
            'id', 'zona', 'zona_codigo', 'metraje', 'precio_base', 'precio',
            'estado', 'area', 'perimetro', 'image', 'linea_base', 'tipo', 'subnivel_de'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class FiltroSerializer(serializers.ModelSerializer):
    zona_codigo = serializers.SerializerMethodField()
    precio = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    perimetro = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    linea_base = serializers.SerializerMethodField()

    class Meta:
        model = Local
        fields = [
            'zona_codigo', 
            'precio', 
            'estado', 
            'area', 
            'perimetro', 
            'image', 
            'linea_base'
        ]

    def get_zona_codigo(self, obj):
        """ Devuelve el código de la zona """
        return obj.zona.codigo

    def get_precio(self, obj):
        """ Devuelve el precio con formato """
        return f"${obj.precio_base.precio:,.2f}" if obj.precio_base else None

    def get_area(self, obj):
        """ Devuelve el área del metraje """
        return f"{obj.metraje.area} m²" if obj.metraje else None

    def get_perimetro(self, obj):
        """ Devuelve el perímetro del metraje """
        return obj.metraje.perimetro if obj.metraje else None

    def get_image(self, obj):
        """ Devuelve la URL de la imagen """
        return obj.metraje.image.url if obj.metraje and obj.metraje.image else None

    def get_linea_base(self, obj):
        """ Devuelve la línea base de la zona """
        return obj.zona.linea_base



class LocalSerializer(serializers.ModelSerializer):
    subniveles = serializers.SerializerMethodField()
    zona = serializers.PrimaryKeyRelatedField(queryset=Zona.objects.all())
    subnivel_de = serializers.PrimaryKeyRelatedField(
        queryset=Local.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Local
        fields = [
            'id',
            'zona',
            'zona_codigo',
            'metraje',
            'precio_base',
            'precio',
            'estado',
            'area',
            'perimetro',
            'image',
            'linea_base',
            'tipo',
            'subnivel_de',
            'subniveles',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['zona_codigo'] = instance.zona.codigo if instance.zona else None
        if instance.precio_base:
            representation['precio'] = f"${instance.precio_base.precio:,.2f}"
        else:
            representation['precio'] = None

        if instance.estado:
            representation['estado'] = instance.estado.capitalize()

        if instance.metraje and instance.metraje.area:
            representation['area'] = f"{instance.metraje.area} m²"
        else:
            representation['area'] = None

        if instance.metraje and instance.metraje.perimetro:
            representation['perimetro'] = instance.metraje.perimetro
        else:
            representation['perimetro'] = None

        representation['image'] = self._get_image_url(instance.metraje)

        # Removemos campos no deseados
        representation.pop('id', None)
        representation.pop('zona', None)
        representation.pop('precio_base', None)
        representation.pop('metraje', None)
        representation.pop('tipo', None)
        representation.pop('subnivel_de', None)

        subniveles = self.get_subniveles(instance)
        if not subniveles:
            representation.pop('subniveles', None)
        else:
            representation['subniveles'] = subniveles

        return representation

    def get_subniveles(self, obj):
        subniveles = obj.subniveles.select_related('zona', 'precio_base', 'metraje').all()
        resultado = []
        for sublocal in subniveles:
            item = {
                "zona_codigo": sublocal.zona.codigo if sublocal.zona else None,
                "precio": f"${sublocal.precio_base.precio:,.2f}" if sublocal.precio_base else None,
                "estado": sublocal.estado.capitalize() if sublocal.estado else None,
                "area": f"{sublocal.metraje.area} m²" if sublocal.metraje and sublocal.metraje.area else None,
                "perimetro": sublocal.metraje.perimetro if sublocal.metraje and sublocal.metraje.perimetro else None,
                "image": self._get_image_url(sublocal.metraje),
                "linea_base": sublocal.zona.linea_base if sublocal.zona else None
            }
            resultado.append(item)
        return resultado

    def _get_image_url(self, metraje):
        if metraje and metraje.image:
            try:
                return metraje.image.url
            except ValueError:
                return None
        return None

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

class GrupoZonaSerializer(serializers.Serializer):
    zona_id = serializers.IntegerField()
    zona_codigo = serializers.CharField()
    linea_base = serializers.CharField()
    locales = serializers.SerializerMethodField()

    def get_locales(self, obj):
        # Obtén los locales relacionados con esta zona
        locales = Local.objects.filter(zona_id=obj['zona_id'])
        return LocalSerializer(locales, many=True).data
    
























