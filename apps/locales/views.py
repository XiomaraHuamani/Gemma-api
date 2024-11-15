from rest_framework import viewsets
from .models import Zona, Metraje, PrecioBase, Descuento, Local, ReciboArras, Cliente
from .serializers import (
    ZonaSerializer, MetrajeSerializer, PrecioBaseSerializer, DescuentoSerializer,
    LocalSerializer, ReciboArrasSerializer, ClienteSerializer
)

class ZonaViewSet(viewsets.ModelViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer


class MetrajeViewSet(viewsets.ModelViewSet):
    queryset = Metraje.objects.all()
    serializer_class = MetrajeSerializer


class PrecioBaseViewSet(viewsets.ModelViewSet):
    queryset = PrecioBase.objects.all()
    serializer_class = PrecioBaseSerializer


class DescuentoViewSet(viewsets.ModelViewSet):
    queryset = Descuento.objects.all()
    serializer_class = DescuentoSerializer


class LocalViewSet(viewsets.ModelViewSet):
    queryset = Local.objects.all()
    serializer_class = LocalSerializer


class ReciboArrasViewSet(viewsets.ModelViewSet):
    queryset = ReciboArras.objects.all()
    serializer_class = ReciboArrasSerializer

    def perform_create(self, serializer):
        # Agregar lógica personalizada si es necesario antes de crear un recibo de arras
        serializer.save()


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
