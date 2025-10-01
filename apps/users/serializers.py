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


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar roles usando enum values.
    """
    class Meta:
        model = Role
        fields = ['name', 'description']


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar usuarios.
    """
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'date_joined', 'is_active']

    def get_role(self, obj):
        """
        Método seguro para obtener el nombre del rol.
        """
        try:
            if hasattr(obj, 'role') and obj.role:
                return obj.role.name
            return None
        except Exception:
            return None


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo de usuario.
    """
    role = serializers.SerializerMethodField(read_only=True)
    role_enum = serializers.CharField(write_only=True, required=False, help_text="Nombre del rol (marketing, asesor, staff, cliente)", source='role_name')
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'role', 'role_enum', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': False}
        }

    def get_role(self, obj):
        """
        Método seguro para obtener el nombre del rol.
        """
        try:
            return obj.role.name if obj.role else None
        except:
            return None

    def to_internal_value(self, data):
        """
        Permite usar tanto 'role' como 'role_enum' para especificar el rol.
        """
        # Si viene 'role' en lugar de 'role_enum', lo renombra
        if 'role' in data and 'role_enum' not in data and not isinstance(data.get('role'), dict):
            data = data.copy()
            data['role_enum'] = data.pop('role')
        return super().to_internal_value(data)

    def create(self, validated_data):
        """
        Sobrescribe el método create para asignar un rol predeterminado si no se proporciona.
        """
        role_enum = validated_data.pop('role_name', None)
        role = None
        
        if role_enum:
            # Busca o crea el rol sin validar si existe
            role, created = Role.objects.get_or_create(name=role_enum)
        else:
            # Si no se especifica un rol, asigna el rol predeterminado (cliente)
            role, created = Role.objects.get_or_create(name=Role.CLIENTE)
        
        # Crea el usuario con el rol asignado
        user = User.objects.create_user(**validated_data, role=role)
        return user

    def update(self, instance, validated_data):
        """
        Sobrescribe el método update para manejar la asignación de rol por enum y actualización de contraseña.
        """
        role_enum = validated_data.pop('role_name', None)
        password = validated_data.pop('password', None)
        
        # Manejar la actualización del rol
        if role_enum:
            # Busca o crea el rol sin validar si existe
            role, created = Role.objects.get_or_create(name=role_enum)
            instance.role = role
        
        # Manejar la actualización de la contraseña
        if password:
            instance.set_password(password)
        
        # Actualizar los demás campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


