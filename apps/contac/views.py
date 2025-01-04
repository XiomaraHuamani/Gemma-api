from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from .models import CpInversion, Contactform
from .serializers import CpInversionSerializer, ContactformSerializer

class CpInversionListCreateView(generics.ListCreateAPIView):
    queryset = CpInversion.objects.all()
    serializer_class = CpInversionSerializer

class CpInversionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CpInversion.objects.all()
    serializer_class = CpInversionSerializer

class ContactformViewSet(ModelViewSet):
    queryset = Contactform.objects.all()
    serializer_class = ContactformSerializer
