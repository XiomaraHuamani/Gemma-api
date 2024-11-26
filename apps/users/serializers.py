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
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'date_joined']  # Campos necesarios
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

