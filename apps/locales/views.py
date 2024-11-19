from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Zona, Metraje, TipoDescuento, PrecioBase, Descuento, Local, ReciboArras, Cliente
from .serializers import (
    ZonaSerializer,
    MetrajeSerializer,
    TipoDescuentoSerializer,
    PrecioBaseSerializer,
    DescuentoSerializer,
    LocalSerializer,
    ReciboArrasSerializer,
    ClienteSerializer,
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


# class DescuentoViewSet(viewsets.ModelViewSet):
#     queryset = Descuento.objects.all()
#     serializer_class = DescuentoSerializer


class DescuentoViewSet(viewsets.ModelViewSet):
    queryset = Descuento.objects.all()
    serializer_class = DescuentoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['zona__codigo'] 



class LocalViewSet(viewsets.ModelViewSet):
    queryset = Local.objects.all()
    serializer_class = LocalSerializer


class ReciboArrasViewSet(viewsets.ModelViewSet):
    queryset = ReciboArras.objects.all()
    serializer_class = ReciboArrasSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
