from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from .models import Zona, Metraje, TipoDescuento, PrecioBase, Descuento, Local, ReciboArras, Cliente, VentaCredito, VentaContado, Pago, Categoria
from .serializers import (
    ZonaSerializer,
    MetrajeSerializer,
    TipoDescuentoSerializer,
    PrecioBaseSerializer,
    DescuentoSerializer,
    LocalSerializer,
    ReciboArrasSerializer,
    ClienteSerializer,
    VentaCreditoSerializer, 
    VentaContadoSerializer, 
    PagoSerializer,
    CategoriaSerializer,
    TipoDescuentoSerializer,
    GruposZonasSerializer,
    SubnivelSerializer
)

from django.apps import apps

Categoria = apps.get_model('locales', 'Categoria')



# class ZonaViewSet(viewsets.ModelViewSet):
#     queryset = Zona.objects.all()
#     serializer_class = ZonaSerializer


class ZonaViewSet(viewsets.ModelViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer

    @action(detail=True, methods=['post'], url_path='add_subniveles')
    def add_subniveles(self, request, pk=None):
        zona = self.get_object()
        if not zona.tiene_subniveles:
            return Response({"detail": "La zona no tiene habilitado subniveles."}, status=status.HTTP_400_BAD_REQUEST)

        subniveles_data = request.data.get('subniveles', [])
        if len(subniveles_data) != 2:
            return Response({"detail": "Debe proporcionar exactamente dos subniveles."}, status=status.HTTP_400_BAD_REQUEST)

        subniveles = []
        for subnivel_data in subniveles_data:
            subnivel_data['subnivel_de'] = zona.id
            subnivel_serializer = LocalSerializer(data=subnivel_data)
            if subnivel_serializer.is_valid():
                subnivel = subnivel_serializer.save()
                subniveles.append(subnivel)
            else:
                return Response(subnivel_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Subniveles creados exitosamente."}, status=status.HTTP_201_CREATED)


class CategoriaViewSet(ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class MetrajeViewSet(viewsets.ModelViewSet):
    queryset = Metraje.objects.all()
    serializer_class = MetrajeSerializer

class TipoDescuentoViewSet(ModelViewSet):
    queryset = TipoDescuento.objects.select_related('categoria').all()
    serializer_class = TipoDescuentoSerializer

class PrecioBaseViewSet(ModelViewSet):
    queryset = PrecioBase.objects.all()
    serializer_class = PrecioBaseSerializer

# class DescuentoViewSet(ModelViewSet):
#     """
#     ViewSet para manejar las operaciones CRUD en Descuento.
#     """
#     queryset = Descuento.objects.select_related('categoria').all()
#     serializer_class = DescuentoSerializer
#     filter_backends = [DjangoFilterBackend]
#     permission_classes = [AllowAny]

class DescuentoViewSet(ModelViewSet):
    queryset = Descuento.objects.select_related('categoria', 'tipo_descuento', 'metraje').all()
    serializer_class = DescuentoSerializer

    def get_serializer_context(self):
        """
        Incluye el contexto de la solicitud en el serializador.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class LocalViewSet(ModelViewSet):
    queryset = Local.objects.all()
    serializer_class = LocalSerializer




class GruposPlazaTecAPIView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Obtiene los locales filtrados por la categoría Plaza Tec (ID=1) y los agrupa por tipo.
        """
        try:
            categoria = Categoria.objects.get(id=1)  # Plaza Tec
            locales = Local.objects.filter(zona__categoria=categoria)

            grupos = {}
            for local in locales:
                tipo_nombre = local.tipo.nombre if local.tipo else "Sin Tipo"  # Obtiene el nombre del tipo
                if tipo_nombre not in grupos:
                    grupos[tipo_nombre] = []
                grupos[tipo_nombre].append(LocalSerializer(local).data)

            grupos_data = [{"tipo": tipo, "locales": locales} for tipo, locales in grupos.items()]

            return Response({"grupos": grupos_data}, status=status.HTTP_200_OK)
        except Categoria.DoesNotExist:
            return Response(
                {"error": "Categoría Plaza Tec no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, *args, **kwargs):
        """
        Permite registrar un local en la categoría Plaza Tec, incluyendo su tipo y subniveles.
        """
        serializer = LocalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LocalesPlazaTecViewSet(ModelViewSet):
    queryset = Local.objects.filter(zona__categoria_id=1).select_related('zona', 'metraje', 'precio_base', 'parent')
    serializer_class = LocalSerializer



class TipoDescuentoPorCategoriaView(APIView):
    def get(self, request, categoria_id):
        """
        Devuelve los tipos de descuento asociados a una categoría específica.
        """
        tipos_descuento = TipoDescuento.objects.filter(categoria_id=categoria_id)
        serializer = TipoDescuentoSerializer(tipos_descuento, many=True)
        return Response(serializer.data)


class ReciboArrasViewSet(ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD en el modelo ReciboArras.
    """
    queryset = ReciboArras.objects.all()
    serializer_class = ReciboArrasSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """
        Lógica adicional al crear un recibo. Rellena campos automáticos.
        """
        serializer.save()

class GruposPorZonaAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Lógica para manejar la solicitud GET
        categoria = Categoria.objects.get(id=1)  # Filtrar por Plaza Tec
        locales = Local.objects.filter(zona__categoria=categoria)
        serializer = GruposZonasSerializer(locales, many=True)
        return Response(serializer.data)




class GruposLocalesAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Obtener todos los locales
        locales = Local.objects.all()

        # Crear un diccionario para agrupar los locales por tipo
        grupos = {}
        for local in locales:
            tipo_nombre = local.tipo if local.tipo else "Sin Tipo"
            if tipo_nombre not in grupos:
                grupos[tipo_nombre] = []

            # Construir la representación del local
            local_data = {
                "zona_codigo": local.zona.codigo,
                "precio": f"${local.precio_base.precio:,.2f}" if local.precio_base else None,
                "estado": local.estado,
                "area": f"{local.metraje.area} m²" if local.metraje else None,
                "altura": f"{local.metraje.altura} m" if local.metraje else None,
                "perimetro": local.metraje.perimetro if local.metraje else None,
                "image": local.metraje.image.url if local.metraje and local.metraje.image else None,
                "linea_base": local.zona.linea_base,
            }

            # Obtener subniveles del local basados en el prefijo del código de zona
            prefijo_zona = local.zona.codigo.split('-')[0]  # Asumimos que el prefijo es antes del guion
            subniveles = Local.objects.filter(zona__codigo__startswith=prefijo_zona).exclude(zona=local.zona)
            
            if subniveles.exists():
                subniveles_data = []
                for subnivel in subniveles:
                    subnivel_data = {
                        "number": subnivel.zona.codigo,
                        "price": f"${subnivel.precio_base.precio:,.2f}" if subnivel.precio_base else None,
                        "status": subnivel.estado,
                        "area": f"{subnivel.metraje.area} m²" if subnivel.metraje else None,
                        "detalle_area": subnivel.metraje.perimetro if subnivel.metraje else None,
                        "img": subnivel.metraje.image.url if subnivel.metraje and subnivel.metraje.image else None,
                    }
                    subniveles_data.append(subnivel_data)
                local_data["subniveles"] = subniveles_data

            # Agregar el local al grupo correspondiente
            grupos[tipo_nombre].append(local_data)

        # Preparar la respuesta con los grupos
        grupos_data = [{"tipo": tipo, "locales": locales} for tipo, locales in grupos.items()]

        return Response({"grupos": grupos_data})


class ClienteViewSet(ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD en el modelo Cliente.
    """
    queryset = Cliente.objects.all().order_by('-fecha_creacion')  # Ordena por la fecha más reciente
    serializer_class = ClienteSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """
        Lógica personalizada al crear un cliente.
        """
        serializer.save()

    def perform_update(self, serializer):
        """
        Lógica personalizada al actualizar un cliente.
        """
        serializer.save()


class VentaCreditoViewSet(ModelViewSet):
    queryset = VentaCredito.objects.select_related('tipo_venta').all()
    serializer_class = VentaCreditoSerializer


class VentaContadoViewSet(ModelViewSet):
    queryset = VentaContado.objects.select_related('tipo_venta', 'descuento').all()
    serializer_class = VentaContadoSerializer


class PagoViewSet(ModelViewSet):
    queryset = Pago.objects.select_related('recibo_arras', 'tipo_venta').all()
    serializer_class = PagoSerializer