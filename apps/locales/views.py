from rest_framework import viewsets, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from .models import Zona, Metraje, TipoDescuento, PrecioBase, Descuento, Local, ReciboArras, Cliente, VentaCredito, VentaContado, Pago, Categoria, SubnivelRelacion

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
    SubnivelRelacionSerializer,
    PlazaTecSerializer,
    GrupoSerializer
)

from django.apps import apps
Categoria = apps.get_model('locales', 'Categoria')


class ZonaViewSet(viewsets.ModelViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer

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

class MetrajeViewSet(viewsets.ModelViewSet):
    queryset = Metraje.objects.all()
    serializer_class = MetrajeSerializer

class TipoDescuentoViewSet(ModelViewSet):
    queryset = TipoDescuento.objects.select_related('categoria').all()
    serializer_class = TipoDescuentoSerializer

class PrecioBaseViewSet(ModelViewSet):
    queryset = PrecioBase.objects.all()
    serializer_class = PrecioBaseSerializer

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

class LocalViewSet(viewsets.ModelViewSet):
    queryset = Local.objects.all()
    serializer_class = LocalSerializer

    def create(self, request, *args, **kwargs):
        # Custom logic can be added here before saving the object
        return super().create(request, *args, **kwargs)

class SubnivelRelacionViewSet(viewsets.ModelViewSet):
    queryset = SubnivelRelacion.objects.select_related(
        'zona_principal', 'subnivel_1', 'subnivel_1__precio_base', 'subnivel_1__metraje',
        'subnivel_2', 'subnivel_2__precio_base', 'subnivel_2__metraje'
    )
    serializer_class = SubnivelRelacionSerializer


    def get_serializer_context(self):
        """
        Pasa el ID de la zona_principal al contexto para que el serializer
        pueda filtrar los locales en subnivel_1 y subnivel_2.
        """
        context = super().get_serializer_context()
        # Pasar zona_principal_id al contexto si está en los datos de la solicitud
        zona_principal_id = self.request.data.get('zona_principal', None)
        if zona_principal_id:
            print(f"Zona Principal ID en Contexto: {zona_principal_id}")
        context['zona_principal_id'] = zona_principal_id
        return context


class PlazaTecView(APIView):
    """
    Vista para generar el JSON estructurado para Plaza Tec.
    """
    def get(self, request):
        # Agrupa los locales por tipo
        tipos = Local.objects.values("tipo").distinct()

        # Serializa los grupos
        grupos = GrupoSerializer(tipos, many=True).data

        # Retorna la respuesta JSON
        return Response({"grupos": grupos})


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