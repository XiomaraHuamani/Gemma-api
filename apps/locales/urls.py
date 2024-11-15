from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ZonaViewSet, MetrajeViewSet, PrecioBaseViewSet, DescuentoViewSet, LocalViewSet, ReciboArrasViewSet, ClienteViewSet

router = DefaultRouter()
router.register(r'zona', ZonaViewSet)
router.register(r'metraje', MetrajeViewSet)
router.register(r'precio_base', PrecioBaseViewSet)
router.register(r'descuento', DescuentoViewSet)
router.register(r'local', LocalViewSet)
router.register(r'recibo_arras', ReciboArrasViewSet)
router.register(r'cliente', ClienteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
