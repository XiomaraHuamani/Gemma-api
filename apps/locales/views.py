from rest_framework import viewsets, status, serializers
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from collections import defaultdict
from rest_framework import generics
from django.db.models import Q
from django.apps import apps
from .models import (
    Zona, 
    TipoDescuento, 
    Descuento, 
    Local, 
    ReciboArras, 
    Cliente, 
    VentaCredito, 
    VentaContado, 
    Pago, 
    Categoria
)
from .serializers import (
    ZonaSerializer,
    TipoDescuentoSerializer,
    DescuentoSerializer,
    LocalSerializer,
    ReciboArrasSerializer,
    ClienteSerializer,
    VentaCreditoSerializer, 
    VentaContadoSerializer, 
    PagoSerializer,
    CategoriaSerializer,
    TipoDescuentoSerializer,
    SimpleLocalSerializer,
    FiltroSerializer,
)

Categoria = apps.get_model('locales', 'Categoria')


class ZonaViewSet(viewsets.ModelViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer

class ListarLocalesAPIView(APIView):
    """
    Endpoint para listar locales por ID en formato de array plano.
    """
    def get(self, request):
        # Obtén todos los locales
        locales = Local.objects.all().order_by('id')
        
        # Serializa los datos usando solo el ID
        locales_data = [{'id': local.id} for local in locales]
        
        return Response(locales_data, status=status.HTTP_200_OK)

class ZonaAPIView(APIView):
    def get(self, request, *args, **kwargs):
        zonas = Zona.objects.all()
        serializer = ZonaSerializer(zonas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = ZonaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoriaViewSet(ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class TipoDescuentoViewSet(ModelViewSet):
    queryset = TipoDescuento.objects.select_related('categoria').all()
    serializer_class = TipoDescuentoSerializer

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


class FiltroView(generics.GenericAPIView):
    """
    Vista para listar y crear locales con campos personalizados.
    """
    serializer_class = FiltroSerializer

    def get_queryset(self):
        """
        Consulta optimizada usando select_related para evitar consultas N+1.
        """
        return Local.objects.select_related(
            'zona',           # FK a Zona
            'precio_base',    # FK a PrecioBase
            'metraje'         # FK a Metraje
        )

    def get(self, request, *args, **kwargs):
        """
        Retorna una lista de locales con campos personalizados.
        """
        locales = self.get_queryset()
        serializer = self.get_serializer(locales, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Crea un nuevo local con campos personalizados.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocalViewSet(ModelViewSet):
    """
    API optimizada para manejar locales con lógica de subniveles.
    """
    queryset = Local.objects.select_related('zona').prefetch_related('subniveles')
    serializer_class = LocalSerializer

class LocalAPIView(APIView):
    """
    API para manejar locales con GET, POST, DELETE y PUT.
    """

    def get(self, request, pk=None):
        """
        Obtiene una lista de todos los locales o un local específico si se proporciona un ID (pk).
        """
        if pk:
            local = get_object_or_404(Local, pk=pk)
            serializer = LocalSerializer(local)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        locales = Local.objects.all()
        serializer = LocalSerializer(locales, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Crea un nuevo local.
        """
        serializer = LocalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        """
        Actualiza un local existente. Requiere el ID (pk) del local.
        """
        if not pk:
            return Response({"error": "El ID del local es necesario para actualizar."}, status=status.HTTP_400_BAD_REQUEST)
        
        local = get_object_or_404(Local, pk=pk)
        serializer = LocalSerializer(local, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """
        Elimina un local existente. Requiere el ID (pk) del local.
        """
        if not pk:
            return Response({"error": "El ID del local es necesario para eliminar."}, status=status.HTTP_400_BAD_REQUEST)
        
        local = get_object_or_404(Local, pk=pk)
        local.delete()
        return Response({"message": "Local eliminado correctamente."}, status=status.HTTP_204_NO_CONTENT)

class ListarLocalesAPIView(APIView):
    """
    Endpoint para listar todos los campos de los locales en formato de array plano.
    """
    def get(self, request):
        locales = Local.objects.all().order_by('id')
        serializer = LocalSerializer(locales, many=True, context={'request': request})  
        return Response(serializer.data, status=status.HTTP_200_OK)

class EditarLocalAPIView(RetrieveUpdateAPIView):
    """
    Endpoint para obtener y editar un local utilizando SimpleLocalSerializer.
    """
    queryset = Local.objects.all()
    serializer_class = SimpleLocalSerializer
    lookup_field = 'pk'


class GruposView(APIView):

    def get(self, request):
        grupos_definidos = [
            {"tipo": "entrada segundaria grupo 1 izquierda", "zona_codigos": ["PT 1", "PT 2", "PT 3", "PT 4", "PT 9", "PT 10", "PT 12", "PT 14"]},
            {"tipo": "entrada segundaria grupo 1 derecha", "zona_codigos": ["PT 5", "PT 6", "PT 7", "PT 8", "PT 15", "PT 16", "PT 18", "PT 20"]},
            {"tipo": "entrada segundaria grupo 2 izquierda", "zona_codigos": ["PT 21", "PT 22", "PT 23", "PT 24", "PT 25", "PT 26", "PT 33", "PT 34"]},
            {"tipo": "entrada segundaria grupo 2 derecha", "zona_codigos": ["PT 27", "PT 28", "PT 29", "PT 30", "PT 31", "PT 32", "PT 37", "PT 38", "PT 93", "PT 40"]},
            {"tipo": "entrada segundaria grupo 3 izquierda", "zona_codigos": ["PT 41", "PT 42", "PT 43", "PT 44", "PT 49", "PT 50", "PT 51", "PT 52", "PT 53", "PT 54"]},
            {"tipo": "entrada segundaria grupo 3 derecha", "zona_codigos": ["PT 45", "PT 46", "PT 47", "PT 48", "PT 55", "PT 56", "PT 47", "PT 58", "PT 59", "PT 60"]},
            {"tipo": "entrada segundaria grupo 4 izquierda", "zona_codigos": ["PT 61", "PT 62", "PT 63", "PT 64", "PT 65", "PT 66", "PT 73", "PT 74", "PT 75", "PT 76", "PT 77", "PT 78"]},
            {"tipo": "entrada segundaria grupo 4 derecha", "zona_codigos": ["PT 67", "PT 68", "PT 69", "PT 70", "PT 71", "PT 72", "PT 79", "PT 80", "PT 81", "PT 82", "PT 83", "PT 84"]},
            {"tipo": "entrada segundaria grupo 5 izquierda", "zona_codigos": ["PT 85", "PT 86", "PT 87", "PT 88", "PT 89", "PT 90", "PT 97", "PT 98", "PT 99", "PT 100"]},
            {"tipo": "entrada segundaria grupo 5 derecha", "zona_codigos": ["PT 91", "PT 92", "PT 93", "PT 94", "PT 95", "PT 96", "PT 101", "PT 102", "PT 103", "PT 104"]},
            {"tipo": "entrada grupo 1 larga", "zona_codigos": ["PT 61", "PT 62", "PT 63", "PT 64", "PT 65", "PT 66", "PT 73", "PT 74", "PT 75", "PT 76", "PT 77", "PT 78"]},
            {"tipo": "entrada grupo 2 larga", "zona_codigos": ["PT 67", "PT 68", "PT 69", "PT 70", "PT 71", "PT 72", "PT 79", "PT 80", "PT 81", "PT 82", "PT 83", "PT 84"]},
        ]

        grupos_response = []

        for grupo_def in grupos_definidos:
            tipo = grupo_def['tipo']
            zona_codigos = grupo_def['zona_codigos']

            # Solo locales principales
            locales_qs = Local.objects.filter(
                zona__codigo__in=zona_codigos,
                estado__in=['Disponible', 'Reservado', 'Vendido'],
                subnivel_de__isnull=True
            ).select_related('zona').prefetch_related('subniveles')

            serializer = LocalSerializer(locales_qs, many=True, context={'request': request})
            grupos_response.append({
                "tipo": tipo,
                "locales": serializer.data
            })

        return Response({"grupos": grupos_response})


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