from rest_framework import serializers
from .models import CpInversion

class CpInversionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CpInversion
        fields = [
            'id',
            'nombre_apellidos',
            'correo_electronico',
            'numero_telefono',
            'dni',
            'objetivo_inversion',
            'mensaje',
            'disponibilidad',
            'fecha_creacion'
        ]
        read_only_fields = ['fecha_creacion']
