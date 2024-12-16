from rest_framework import serializers
from .models import Zona, Metraje, TipoDescuento, PrecioBase, Descuento, Local, ReciboArras, Cliente, Pago, VentaContado, VentaCredito, Categoria 
from decimal import Decimal


class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = ['id', 'categoria', 'codigo', 'linea_base', 'tiene_subniveles']
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


# class LocalSerializer(serializers.ModelSerializer):
#     subnivel_de = serializers.PrimaryKeyRelatedField(
#         queryset=Zona.objects.none(),  # Inicialización vacía
#         required=False,
#         allow_null=True
#     )

#     zona = serializers.PrimaryKeyRelatedField(
#         queryset=Zona.objects.all()
#     )
#     precio_base = serializers.PrimaryKeyRelatedField(
#         queryset=PrecioBase.objects.all(),
#         required=False,
#         allow_null=True
#     )
#     metraje = serializers.PrimaryKeyRelatedField(
#         queryset=Metraje.objects.all()
#     )

#     class Meta:
#         model = Local
#         fields = [
#             'id', 'zona', 'zona_codigo', 'metraje', 'precio_base',
#             'precio', 'estado', 'area', 'perimetro', 'image',
#             'linea_base', 'tipo', 'subnivel_de'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Filtra dinámicamente solo zonas con subniveles habilitados
#         self.fields['subnivel_de'].queryset = Zona.objects.filter(tiene_subniveles=True)


#     def to_representation(self, instance):
#         """ Representación personalizada para incluir detalles extra sobre los campos relacionados. """
#         representation = super().to_representation(instance)
#         representation['zona_codigo'] = instance.zona.codigo
#         representation['precio'] = instance.precio_base.precio if instance.precio_base else None
#         representation['area'] = instance.metraje.area if instance.metraje else None
#         representation['perimetro'] = instance.metraje.perimetro if instance.metraje else None
#         representation['image'] = instance.metraje.image.url if instance.metraje and instance.metraje.image else None
#         representation['linea_base'] = instance.zona.linea_base
#         return representation

class LocalSerializer(serializers.ModelSerializer):
    subnivel_de = serializers.PrimaryKeyRelatedField(
        queryset=Local.objects.none(),  # Se inicializa vacío
        required=False,
        allow_null=True
    )

    zona = serializers.PrimaryKeyRelatedField(
        queryset=Zona.objects.all()
    )
    precio_base = serializers.PrimaryKeyRelatedField(
        queryset=PrecioBase.objects.all(),
        required=False,
        allow_null=True
    )
    metraje = serializers.PrimaryKeyRelatedField(
        queryset=Metraje.objects.all()
    )

    class Meta:
        model = Local
        fields = [
            'id', 'zona', 'zona_codigo', 'metraje', 'precio_base',
            'precio', 'estado', 'area', 'perimetro', 'image',
            'linea_base', 'tipo', 'subnivel_de'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra dinámicamente solo locales con subniveles habilitados
        self.fields['subnivel_de'].queryset = Local.objects.filter(
            subnivel_de__isnull=True, zona__tiene_subniveles=True, estado='disponible'
        )

    def to_representation(self, instance):
        """ Representación personalizada para incluir detalles extra sobre los campos relacionados. """
        representation = super().to_representation(instance)
        representation['zona_codigo'] = instance.zona.codigo
        representation['precio'] = f"${instance.precio_base.precio:,.2f}" if instance.precio_base else None
        representation['area'] = instance.metraje.area if instance.metraje else None
        representation['perimetro'] = instance.metraje.perimetro if instance.metraje else None
        representation['image'] = instance.metraje.image.url if instance.metraje and instance.metraje.image else None
        representation['linea_base'] = instance.zona.linea_base

        # Incluye subniveles si existen
        subniveles = instance.subniveles.all()
        if subniveles.exists():
            representation['subniveles'] = [
                {
                    "zona_codigo": sublocal.zona.codigo,
                    "precio": f"${sublocal.precio_base.precio:,.2f}" if sublocal.precio_base else None,
                    "estado": sublocal.estado.capitalize(),
                    "area": sublocal.metraje.area if sublocal.metraje else None,
                    "perimetro": sublocal.metraje.perimetro if sublocal.metraje else None,
                    "image": sublocal.metraje.image.url if sublocal.metraje and sublocal.metraje.image else None,
                    "linea_base": sublocal.zona.linea_base
                }
                for sublocal in subniveles
            ]
        return representation

    def validate(self, data):
        """ Personaliza la validación para asegurar coherencia entre `zona` y `subnivel_de`. """
        subnivel_de = data.get('subnivel_de')
        if subnivel_de and not subnivel_de.zona.tiene_subniveles:
            raise serializers.ValidationError({
                'subnivel_de': 'El local seleccionado no pertenece a una zona con subniveles habilitados.'
            })
        return data

from rest_framework import serializers

class SubnivelSerializer(serializers.ModelSerializer):
    zona_codigo = serializers.CharField(source='zona.codigo')
    precio = serializers.SerializerMethodField()
    area = serializers.CharField(source='metraje.area', read_only=True)
    perimetro = serializers.CharField(source='metraje.perimetro', read_only=True)
    image = serializers.ImageField(source='metraje.image', read_only=True)
    linea_base = serializers.CharField(source='zona.linea_base', read_only=True)

    class Meta:
        model = Local
        fields = [
            'zona_codigo', 'precio', 'estado', 'area', 'perimetro', 'image', 'linea_base'
        ]

    def get_precio(self, obj):
        return f"${obj.precio_base.precio:,.2f}" if obj.precio_base else None


class GruposSerializer(serializers.ModelSerializer):
    zona_codigo = serializers.CharField(source='zona.codigo')
    precio = serializers.SerializerMethodField()
    area = serializers.CharField(source='metraje.area', read_only=True)
    perimetro = serializers.CharField(source='metraje.perimetro', read_only=True)
    image = serializers.ImageField(source='metraje.image', read_only=True)
    linea_base = serializers.CharField(source='zona.linea_base', read_only=True)
    subniveles = serializers.SerializerMethodField()

    class Meta:
        model = Local
        fields = [
            'zona_codigo', 'precio', 'estado', 'area', 'perimetro', 'image', 'linea_base', 'subniveles'
        ]

    def get_precio(self, obj):
        return f"${obj.precio_base.precio:,.2f}" if obj.precio_base else None

    def get_subniveles(self, obj):
        """ Obtener subniveles asociados """
        subniveles = Local.objects.filter(subnivel_de=obj)
        return SubnivelSerializer(subniveles, many=True).data



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
    
























