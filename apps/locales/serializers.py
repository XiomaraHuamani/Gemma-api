from rest_framework import serializers
from .models import Zona, Metraje, TipoDescuento, PrecioBase, Descuento, Local, ReciboArras, Cliente, Pago, VentaContado, VentaCredito, Categoria, SubnivelRelacion 
from decimal import Decimal


# class ZonaSerializer(serializers.ModelSerializer):
#     locales = serializers.SerializerMethodField()

#     class Meta:
#         model = Zona
#         fields = ['id', 'categoria', 'codigo', 'linea_base', 'tiene_subniveles', 'locales']

#     def get_locales(self, obj):
#         # Obtener locales de una zona
#         locales = Local.objects.filter(zona=obj)
#         return LocalSerializer(locales, many=True).data


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

class SubnivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Local
        fields = [
            "zona_codigo",
            "precio",
            "estado",
            "area",
            "altura",
            "perimetro",
            "image",
            "linea_base",
        ]
        extra_kwargs = {
            "zona_codigo": {"source": "codigo"},
            "precio": {"source": "precio_base.precio"},
            "area": {"source": "metraje.area"},
            "altura": {"source": "metraje.altura"},
            "perimetro": {"source": "metraje.perimetro"},
            "image": {"source": "metraje.image.url"},
            "linea_base": {"source": "zona.linea_base"},
        }

  
class SubnivelRelacionSerializer(serializers.ModelSerializer):
    zona_principal_codigo = serializers.CharField(source='zona_principal.codigo')  # Usar código en lugar de ID para la zona principal
    subnivel_1_codigo = serializers.SlugRelatedField(
        queryset=Local.objects.all(),
        slug_field='codigo',  # Relacionar usando el campo `codigo` del modelo Local
        source='subnivel_1'
    )
    subnivel_2_codigo = serializers.SlugRelatedField(
        queryset=Local.objects.all(),
        slug_field='codigo',  # Relacionar usando el campo `codigo` del modelo Local
        source='subnivel_2'
    )

    class Meta:
        model = SubnivelRelacion
        fields = ['id', 'zona_principal_codigo', 'subnivel_1_codigo', 'subnivel_2_codigo']

    def validate(self, data):
        # Validar que la zona principal existe y tiene subniveles habilitados
        try:
            zona_principal = Zona.objects.get(codigo=data['zona_principal']['codigo'])
        except Zona.DoesNotExist:
            raise serializers.ValidationError("La zona principal especificada no existe.")

        if not zona_principal.tiene_subniveles:
            raise serializers.ValidationError("La zona especificada no tiene habilitada la opción de subniveles.")

        return data

    def create(self, validated_data):
        # Obtener objetos de la base de datos
        zona_principal = Zona.objects.get(codigo=validated_data['zona_principal']['codigo'])
        subnivel_1 = validated_data['subnivel_1']
        subnivel_2 = validated_data['subnivel_2']

        # Crear la relación de subniveles
        subnivel_relacion = SubnivelRelacion.objects.create(
            zona_principal=zona_principal,
            subnivel_1=subnivel_1,
            subnivel_2=subnivel_2
        )
        return subnivel_relacion


class LocalSerializer(serializers.ModelSerializer):
    zona_codigo = serializers.CharField(source='zona.codigo', read_only=True)
    zona_id = serializers.PrimaryKeyRelatedField(queryset=Zona.objects.all(), source='zona', write_only=True)
    metraje_id = serializers.PrimaryKeyRelatedField(queryset=Metraje.objects.all(), source='metraje', write_only=True)
    precio_base_id = serializers.PrimaryKeyRelatedField(queryset=PrecioBase.objects.all(), source='precio_base', write_only=True)

    class Meta:
        model = Local
        fields = [
            'id', 'zona_codigo', 'zona_id', 'metraje_id', 'estado', 'precio_base_id', 'tipo'
        ]
        extra_kwargs = {
            'estado': {'required': True},
            'tipo': {'required': False, 'allow_blank': True},
        }

class GruposPlazaTecSerializer(serializers.Serializer):
    tipo = serializers.CharField()
    locales = LocalSerializer(many=True)

class LocalSerializerWithSubniveles(serializers.Serializer):
    zona_codigo = serializers.CharField(source="zona.codigo")
    precio = serializers.SerializerMethodField()
    estado = serializers.CharField()
    area = serializers.CharField(source="metraje.area", allow_null=True)
    altura = serializers.CharField(source="metraje.altura", allow_null=True)
    perimetro = serializers.CharField(source="metraje.perimetro", allow_null=True)
    image = serializers.SerializerMethodField()
    linea_base = serializers.CharField(source="zona.linea_base")
    subniveles = SubnivelSerializer(many=True, required=True)

    def get_precio(self, obj):
        return f"${obj.precio_base.precio:,.2f}" if obj.precio_base else None

    def get_image(self, obj):
        return obj.metraje.image.url if obj.metraje and obj.metraje.image else None

class LocalSerializerWithSubniveles(serializers.Serializer):
    zona_codigo = serializers.CharField()
    precio_base = serializers.PrimaryKeyRelatedField(queryset=PrecioBase.objects.all())
    estado = serializers.CharField()
    metraje = serializers.PrimaryKeyRelatedField(queryset=Metraje.objects.all())
    subniveles = serializers.ListSerializer(
        child=serializers.DictField(),
        required=False,
        allow_null=True
    )

class GruposZonasSerializer(serializers.Serializer):
    tipo = serializers.CharField()
    locales = LocalSerializerWithSubniveles(many=True)

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
    
























