from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, RoleViewSet, UserViewSet

# Configuración del router para los endpoints basados en vistas
router = DefaultRouter()
router.register('roles', RoleViewSet, basename='roles')
router.register('users', UserViewSet, basename='users')  # CRUD para usuarios

# Definición de URLs
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # Endpoint de registro
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login con JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresco del token
    path('', include(router.urls)),  # Incluye rutas generadas automáticamente
]
