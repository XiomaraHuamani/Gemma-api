from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role

User = get_user_model()

class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Role.
    """
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo de usuario.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'date_joined']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Sobrescribe el método create para asignar un rol predeterminado si no se proporciona.
        """
        role = validated_data.pop('role', None)
        if not role:
            # Si no se especifica un rol, asigna el rol predeterminado (por ejemplo, 'cliente')
            role = Role.objects.get_or_create(name=Role.CLIENTE)[0]
        
        # Crea el usuario con el rol asignado
        user = User.objects.create_user(**validated_data, role=role)
        return user


