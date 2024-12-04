from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ZonaViewSet,
    CategoriaViewSet,
    MetrajeViewSet,
    TipoDescuentoViewSet,
    PrecioBaseViewSet,
    DescuentoViewSet,
    LocalViewSet,
    ReciboArrasViewSet,
    ClienteViewSet,
    VentaCreditoViewSet, 
    VentaContadoViewSet, 
    PagoViewSet,
    TipoDescuentoPorCategoriaView,
    GruposPorZonaAPIView,
    GruposPlazaTecAPIView,
    LocalesPlazaTecViewSet,
    GruposLocalesAPIView
)

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'zonas', ZonaViewSet, basename='zona')
router.register(r'metrajes', MetrajeViewSet)
router.register(r'tipo-descuento', TipoDescuentoViewSet, basename='tipo-descuento')
router.register(r'descuentos', DescuentoViewSet)
router.register(r'precios-base', PrecioBaseViewSet, basename='precios-base')
router.register(r'locales', LocalViewSet, basename='local')
router.register(r'recibos-arras', ReciboArrasViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'ventas-credito', VentaCreditoViewSet, basename='venta-credito')
router.register(r'ventas-contado', VentaContadoViewSet, basename='venta-contado')
router.register(r'pagos', PagoViewSet, basename='pago')
router.register(r'grupos-tec', LocalesPlazaTecViewSet, basename='grupos-tec')


urlpatterns = [
    path('', include(router.urls)),
    path('tipo-descuento-por-categoria/<int:categoria_id>/', TipoDescuentoPorCategoriaView.as_view(), name='tipo-descuento-por-categoria'),
    #path('grupos-zonas/', GruposPorZonaAPIView.as_view(), name='grupos-zonas'),
    path('grupos/', GruposLocalesAPIView.as_view(), name='grupos-locales'),
]
