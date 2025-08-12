from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomTokenObtainPairView, TestView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, RoleViewSet, UserViewSet

# Configurar el router
router = DefaultRouter()
router.register('roles', RoleViewSet, basename='roles')
router.register('users', UserViewSet, basename='users')  

# URLs del router (estas deben ir primero)
router_urls = router.urls

# URLs específicas
specific_urls = [
    path('test/', TestView.as_view(), name='test'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
]

# Combinar todas las URLs
urlpatterns = router_urls + specific_urls
