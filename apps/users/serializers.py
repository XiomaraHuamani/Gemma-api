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
    Serializador para el modelo de usuario.
    """
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        required=True,  # Asegúrate de que sea obligatorio
        help_text="El rol asignado al usuario."
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'date_joined': {'read_only': True},
        }

    def create(self, validated_data):
        """
        Crear un usuario con contraseña encriptada y asignar rol.
        """
        password = validated_data.pop('password', None)
        role = validated_data.pop('role', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        if role:
            user.role = role
            user.save()
        return user

