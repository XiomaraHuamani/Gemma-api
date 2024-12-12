from rest_framework import serializers
from .models import Zona, Metraje, TipoDescuento, PrecioBase, Descuento, Local, ReciboArras, Cliente, Pago, VentaContado, VentaCredito, Categoria 
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




class LocalSerializer(serializers.ModelSerializer):
    zona_codigo = serializers.CharField(source='zona.codigo', read_only=True)
    precio = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    perimetro = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    subniveles = serializers.SerializerMethodField()

    class Meta:
        model = Local
        fields = [
            'zona_codigo',
            'estado',
            'precio',
            'area',
            'perimetro',
            'image',
            'subniveles'
        ]

    def get_precio(self, obj):
        return f"${obj.precio_base.precio:.2f}" if obj.precio_base else "No definido"

    def get_area(self, obj):
        return f"{obj.metraje.area} m²" if obj.metraje else "No definido"

    def get_perimetro(self, obj):
        return obj.metraje.perimetro if obj.metraje else "No definido"

    def get_image(self, obj):
        # Aquí puedes personalizar la lógica para determinar la imagen
        return "../assets/tipos_locales/mediano.png"

    def get_subniveles(self, obj):
        # Filtrar subniveles relacionados usando el prefijo del código de zona
        subniveles = Local.objects.filter(
            zona__codigo__startswith=obj.zona.codigo,
            tipo=None  # Asume que los subniveles no tienen un tipo asignado
        ).exclude(id=obj.id)  # Excluir el propio local

        # Serializar los subniveles
        return [
            {
                "subnivel": sub.zona.codigo,
                "precio": self.get_precio(sub),
                "estado": sub.estado,
                "area": self.get_area(sub),
                "perimetro": self.get_perimetro(sub),
                "image": self.get_image(sub),
            }
            for sub in subniveles
        ]


    
class GrupoSerializer(serializers.Serializer):
    tipo = serializers.CharField()
    locales = LocalSerializer(many=True)

class GruposSerializer(serializers.Serializer):
    grupos = serializers.SerializerMethodField()

    def get_grupos(self, obj):
        tipos = Local.objects.values_list("tipo", flat=True).distinct()
        grupos = []
        for tipo in tipos:
            grupo = {
                "tipo": tipo,
                "locales": GrupoSerializer({"tipo": tipo}).data.get("locales", []),
            }
            grupos.append(grupo)
        return grupos
    




class LocalDetailSerializer(serializers.ModelSerializer):
    zona_codigo = serializers.CharField(source="zona.codigo", read_only=True)
    precio = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    perimetro = serializers.SerializerMethodField()
    linea_base = serializers.CharField(source="zona.linea_base", read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Local
        fields = [
            "zona_codigo",
            "precio",
            "estado",
            "area",
            "perimetro",
            "image",
            "linea_base",
        ]

    def get_precio(self, obj):
        return f"${obj.precio_base.precio}" if obj.precio_base else "N/A"

    def get_area(self, obj):
        return f"{obj.metraje.area} m²" if obj.metraje else "N/A"

    def get_perimetro(self, obj):
        return obj.metraje.perimetro if obj.metraje else "N/A"

    def get_image(self, obj):
        return "../assets/tipos_locales/default.png"





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
    
























