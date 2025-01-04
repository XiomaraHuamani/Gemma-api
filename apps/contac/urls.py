from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CpInversionListCreateView, CpInversionRetrieveUpdateDestroyView, ContactformViewSet

router = DefaultRouter()
router.register(r'contactform', ContactformViewSet, basename='contactform')


urlpatterns = [
    path('cpinversion/', CpInversionListCreateView.as_view(), name='cpinversion-list-create'),
    path('cpinversion/<int:pk>/', CpInversionRetrieveUpdateDestroyView.as_view(), name='cpinversion-detail'),
] + router.urls
