from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ZonaViewSet,
    MetrajeViewSet,
    TipoDescuentoViewSet,
    PrecioBaseViewSet,
    DescuentoViewSet,
    LocalViewSet,
    ReciboArrasViewSet,
    ClienteViewSet,
)

router = DefaultRouter()
router.register(r'zonas', ZonaViewSet)
router.register(r'metrajes', MetrajeViewSet)
router.register(r'tipos-descuento', TipoDescuentoViewSet)
router.register(r'precios-base', PrecioBaseViewSet)
router.register(r'descuentos', DescuentoViewSet)
router.register(r'locales', LocalViewSet)
router.register(r'recibos-arras', ReciboArrasViewSet)
router.register(r'clientes', ClienteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
