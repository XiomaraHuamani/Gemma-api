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
            'tipo_local',
            'objetivo_inversion',
            'mensaje',
            'acepta_terminos',
            'fecha_creacion'
        ]
        read_only_fields = ['fecha_creacion']  # Solo lectura para la fecha
