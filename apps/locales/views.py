from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
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



class ZonaViewSet(viewsets.ModelViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer

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
        try:
            categoria = Categoria.objects.get(id=1)  # Plaza Tec
            locales = Local.objects.filter(zona__categoria=categoria)

            grupos = {}
            for local in locales:
                tipo_nombre = local.tipo.nombre if local.tipo else "Sin Tipo"
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
        Permite registrar un local, incluyendo su tipo y subniveles.
        """
        serializer = LocalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocalesPlazaTecViewSet(ModelViewSet):
    queryset = Local.objects.filter(zona__categoria_id=1).select_related('zona', 'metraje', 'tipo', 'parent')
    serializer_class = LocalSerializer

    def create(self, request, *args, **kwargs):
        """
        Permite la creación de locales con subniveles y tipos definidos.
        """
        return super().create(request)

    def list(self, request, *args, **kwargs):
        """
        Lista los locales filtrados por categoría Plaza Tec (ID=1).
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
