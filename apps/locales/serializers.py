from rest_framework import serializers
from .models import Zona, Metraje, TipoDescuento, PrecioBase, Descuento, Local, ReciboArras, Cliente, Pago, VentaContado, VentaCredito, Categoria, SubnivelRelacion, Subnivel 
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


class SubnivelRelacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubnivelRelacion
        fields = ['id', 'zona_principal', 'subnivel_1', 'subnivel_2', 'permitir_zonas_diferentes']

    def to_representation(self, instance):
        """
        Personaliza la representación del objeto para anidar los subniveles.
        """
        representation = {
            "zona_principal": instance.zona_principal.codigo,
            "subniveles": [
                {
                    "subnivel_1": instance.subnivel_1.zona.codigo,
                    "precio_base": f"${instance.subnivel_1.precio_base.precio if instance.subnivel_1.precio_base else 'N/A'}",
                    "estado": instance.subnivel_1.estado,
                    "area": f"{instance.subnivel_1.metraje.area} m²",
                    "perimetro": instance.subnivel_1.metraje.perimetro if instance.subnivel_1.metraje else "N/A",
                    "image": "../assets/tipos_locales/mediano.png",  # Puedes ajustar esto según la lógica de tu proyecto
                },
                {
                    "subnivel_2": instance.subnivel_2.zona.codigo,
                    "precio_base": f"${instance.subnivel_2.precio_base.precio if instance.subnivel_2.precio_base else 'N/A'}",
                    "estado": instance.subnivel_2.estado,
                    "area": f"{instance.subnivel_2.metraje.area} m²",
                    "perimetro": instance.subnivel_2.metraje.perimetro if instance.subnivel_2.metraje else "N/A",
                    "image": "../assets/tipos_locales/mediano.png",  # Puedes ajustar esto según la lógica de tu proyecto
                }
            ]
        }
        return representation

    class Meta:
        model = SubnivelRelacion
        fields = ['id', 'zona_principal', 'subnivel_1', 'subnivel_2', 'permitir_zonas_diferentes']
        read_only_fields = ['id']

    def validate(self, data):
        """
        Validación adicional para asegurar que subnivel_1 y subnivel_2 sean válidos
        y respeten la configuración de zonas.
        """
        zona_principal = data['zona_principal']
        subnivel_1 = data['subnivel_1']
        subnivel_2 = data['subnivel_2']
        permitir_zonas_diferentes = data.get('permitir_zonas_diferentes', False)

        # Validar zonas solo si permitir_zonas_diferentes es False
        if not permitir_zonas_diferentes:
            if subnivel_1.zona != zona_principal or subnivel_2.zona != zona_principal:
                raise serializers.ValidationError(
                    "Ambos subniveles deben pertenecer a la zona principal seleccionada."
                )
        
        # Verificar que subnivel_1 y subnivel_2 sean diferentes
        if subnivel_1 == subnivel_2:
            raise serializers.ValidationError("Los subniveles deben ser diferentes.")
        
        return data

# class LocalSerializer(serializers.ModelSerializer):
#     zona_codigo = serializers.CharField(source='zona.codigo', read_only=True)
#     zona_id = serializers.PrimaryKeyRelatedField(queryset=Zona.objects.all(), source='zona', write_only=True)
#     metraje_id = serializers.PrimaryKeyRelatedField(queryset=Metraje.objects.all(), source='metraje', write_only=True)
#     precio_base_id = serializers.PrimaryKeyRelatedField(queryset=PrecioBase.objects.all(), source='precio_base', write_only=True)

#     class Meta:
#         model = Local
#         fields = [
#             'id', 'zona_codigo', 'zona_id', 'metraje_id', 'estado', 'precio_base_id', 'tipo'
#         ]
#         extra_kwargs = {
#             'estado': {'required': True},
#             'tipo': {'required': False, 'allow_blank': True},
#         }

# class LocalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Local
#         fields = ['id', 'zona', 'metraje', 'estado', 'precio_base', 'tipo']

#     def validate(self, data):
#         # Verificar si ya existe un local con la misma zona y metraje
#         zona = data.get('zona')
#         metraje = data.get('metraje')
#         if Local.objects.filter(zona=zona, metraje=metraje).exclude(id=self.instance.id if self.instance else None).exists():
#             raise serializers.ValidationError(
#                 "Ya existe un local con esta combinación de zona y metraje."
#             )
#         return data


#---------------------serializer de subniveles-------------------------------------------
# class SubnivelSerializer(serializers.ModelSerializer):
#     subnivel = serializers.CharField(source="zona.codigo")
#     precio = serializers.SerializerMethodField()
#     estado = serializers.CharField()
#     area = serializers.SerializerMethodField()
#     altura = serializers.SerializerMethodField()
#     perimetro = serializers.CharField(source="metraje.perimetro", default=None)
#     image = serializers.SerializerMethodField()

#     class Meta:
#         model = SubnivelRelacion
#         fields = ["subnivel", "precio", "estado", "area", "altura", "perimetro", "image"]

#     def get_precio(self, obj):
#         # Si no existe una relación con precio_base, ajusta este método.
#         if obj.precio_base:
#             return f"${obj.precio_base.precio:.2f}"
#         return None

#     def get_area(self, obj):
#         if obj.metraje:
#             return f"{obj.metraje.area} m²"
#         return None

#     def get_altura(self, obj):
#         return "4.5 m"

#     def get_image(self, obj):
#         return "../assets/tipos_locales/mediano.png"

# class LocalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Local
#         fields = ['id', 'zona', 'metraje', 'estado', 'precio_base', 'tipo']
#---------------------serializer de subniveles-------------------------------------------

class SubnivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subnivel
        fields = ['zona', 'precio_base', 'estado', 'metraje', 'image']

class LocalSerializer(serializers.ModelSerializer):
    subniveles = SubnivelSerializer(many=True, required=False)

    class Meta:
        model = Local
        fields = ['id', 'zona', 'metraje', 'estado', 'precio_base', 'tipo', 'subniveles']

    def create(self, validated_data):
        subniveles_data = validated_data.pop('subniveles', [])
        local = Local.objects.create(**validated_data)
        for subnivel_data in subniveles_data:
            Subnivel.objects.create(local_principal=local, **subnivel_data)
        return local

    def update(self, instance, validated_data):
        subniveles_data = validated_data.pop('subniveles', [])
        instance = super().update(instance, validated_data)

        # Actualizar o crear subniveles
        for subnivel_data in subniveles_data:
            subnivel, created = Subnivel.objects.update_or_create(
                local_principal=instance,
                zona=subnivel_data['zona'],
                defaults=subnivel_data
            )
        return instance


#     def validate(self, data):
#         # Verificar si ya existe un local con la misma zona y metraje
#         zona = data.get('zona')
#         metraje = data.get('metraje')
#         if Local.objects.filter(zona=zona, metraje=metraje).exclude(id=self.instance.id if self.instance else None).exists():
#             raise serializers.ValidationError(
#                 "Ya existe un local con esta combinación de zona y metraje."
#             )
#         return data


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


    
class LocalWithSubnivelesSerializer(serializers.ModelSerializer):
    zona_codigo = serializers.CharField(source="zona.codigo")
    subniveles = serializers.SerializerMethodField()

    class Meta:
        model = Local
        fields = ["zona_codigo", "subniveles"]

    def get_subniveles(self, obj):
        subniveles = SubnivelRelacion.objects.filter(zona_principal=obj.zona)
        if not subniveles.exists():
            return None  # Retornar None si no hay subniveles
        serializer = SubnivelSerializer(subniveles, many=True)
        return serializer.data



    tipo = serializers.CharField()
    locales = serializers.SerializerMethodField()

    def get_locales(self, obj):
        locales = Local.objects.filter(tipo=obj["tipo"])
        locales_data = LocalSerializer(locales, many=True).data

        subniveles = SubnivelRelacion.objects.filter(subnivel_1__tipo=obj["tipo"])
        subniveles_data = SubnivelSerializer(subniveles, many=True).data

        return locales_data + subniveles_data

    
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
    

# class GrupoSerializer(serializers.Serializer):
#     """
#     Serializador para agrupar los locales por tipo.
#     """
#     tipo = serializers.CharField()
#     locales = serializers.SerializerMethodField()

#     def get_locales(self, obj):
#         # Filtra los locales por tipo
#         locales = Local.objects.filter(tipo=obj["tipo"])
#         subniveles = SubnivelRelacion.objects.filter(zona_principal__codigo=obj["tipo"])

#         local_serializer = LocalDetailSerializer(locales, many=True)
#         subnivel_serializer = SubnivelSerializer(subniveles, many=True)

#         # Combina locales y subniveles
#         return local_serializer.data + subnivel_serializer.data


class PlazaTecSerializer(serializers.ModelSerializer):
    """
    Serializador para representar zonas principales con subniveles.
    """
    zona_principal = serializers.CharField(source="zona_principal.codigo", read_only=True)
    subniveles = serializers.SerializerMethodField()

    class Meta:
        model = SubnivelRelacion
        fields = ["zona_principal", "subniveles"]

    def get_subniveles(self, obj):
        # Filtra los subniveles relacionados con la zona principal
        subniveles = SubnivelRelacion.objects.filter(zona_principal=obj.zona_principal)
        return SubnivelSerializer(subniveles, many=True).data



    def get_grupos(self, obj):
        tipos = Local.objects.values("tipo").distinct()  # Agrupar por tipos
        grupos = []

        for tipo in tipos:
            locales = Local.objects.filter(tipo=tipo["tipo"])
            grupo = {
                "tipo": tipo["tipo"],
                "locales": LocalDetailSerializer(locales, many=True).data,
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
    
























