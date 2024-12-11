from django.urls import path
from .views import CpInversionListCreateView

urlpatterns = [
    path('cpinversion/', CpInversionListCreateView.as_view(), name='cpinversion-list-create'),
]
