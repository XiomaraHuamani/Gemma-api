from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ZonaViewSet,
    CategoriaViewSet,
    TipoDescuentoViewSet,
    DescuentoViewSet,
    ReciboArrasViewSet,
    ClienteViewSet,
    VentaCreditoViewSet, 
    VentaContadoViewSet, 
    PagoViewSet,
    TipoDescuentoPorCategoriaView,
    GruposView,
    LocalViewSet,
    ListarLocalesAPIView,
    EditarLocalAPIView,
    FiltroView,
    LocalAPIView,
    
)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'zonas', ZonaViewSet, basename='zona')
router.register(r'tipo-descuento', TipoDescuentoViewSet, basename='tipo-descuento')
router.register(r'descuentos', DescuentoViewSet)
router.register(r'recibos-arras', ReciboArrasViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'ventas-credito', VentaCreditoViewSet, basename='venta-credito')
router.register(r'ventas-contado', VentaContadoViewSet, basename='venta-contado')
router.register(r'pagos', PagoViewSet, basename='pago')
router.register(r'locales', LocalViewSet, basename='local')



urlpatterns = [
    path('', include(router.urls)),
    path('tipo-descuento-por-categoria/<int:categoria_id>/', TipoDescuentoPorCategoriaView.as_view(), name='tipo-descuento-por-categoria'),
    path('locales-l/listar/', ListarLocalesAPIView.as_view(), name='listar-locales'),
    path('locales-l/editar/<int:pk>/', EditarLocalAPIView.as_view(), name='editar-local'),
    path("grupos/", GruposView.as_view(), name="grupos"),
    path("filtros/", FiltroView.as_view(), name="filtros"),
    
]
