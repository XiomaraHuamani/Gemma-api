from django.urls import path
from .views import CpInversionListCreateView, CpInversionRetrieveUpdateDestroyView

urlpatterns = [
    path('cpinversion/', CpInversionListCreateView.as_view(), name='cpinversion-list-create'),
    path('cpinversion/<int:pk>/', CpInversionRetrieveUpdateDestroyView.as_view(), name='cpinversion-detail'),
]
