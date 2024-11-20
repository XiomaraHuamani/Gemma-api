from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Zona, Metraje, TipoDescuento, PrecioBase, Descuento, Local, ReciboArras, Cliente, VentaCredito, VentaContado, Pago
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
    PagoSerializer
)


class ZonaViewSet(viewsets.ModelViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer


class MetrajeViewSet(viewsets.ModelViewSet):
    queryset = Metraje.objects.all()
    serializer_class = MetrajeSerializer


class TipoDescuentoViewSet(viewsets.ModelViewSet):
    queryset = TipoDescuento.objects.all()
    serializer_class = TipoDescuentoSerializer


class PrecioBaseViewSet(viewsets.ModelViewSet):
    queryset = PrecioBase.objects.all()
    serializer_class = PrecioBaseSerializer

class DescuentoViewSet(ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD en Descuento.
    """
    queryset = Descuento.objects.all()
    serializer_class = DescuentoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['zona__codigo'] 
    permission_classes = [AllowAny] 



class LocalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD en Descuento.
    """
    queryset = Local.objects.all()
    serializer_class = LocalSerializer
    permission_classes = [AllowAny] 


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
