from rest_framework import generics
from .models import CpInversion
from .serializers import CpInversionSerializer

class CpInversionListCreateView(generics.ListCreateAPIView):
    queryset = CpInversion.objects.all()
    serializer_class = CpInversionSerializer

class CpInversionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CpInversion.objects.all()
    serializer_class = CpInversionSerializer
