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
    name = serializers.ChoiceField(choices=Role.ROLE_CHOICES, help_text="Nombre del rol (marketing, asesor, staff, cliente)")
    
    class Meta:
        model = Role
        fields = ['name', 'description']

    def validate_name(self, value):
        """
        Valida que el nombre del rol sea único.
        """
        if Role.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"Ya existe un rol con el nombre '{value}'.")
        return value


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar usuarios.
    """
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'date_joined', 'is_active']

    def get_role(self, obj):
        """
        Método seguro para obtener el nombre del rol.
        """
        try:
            return obj.role.name if obj.role else None
        except:
            return None


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo de usuario.
    """
    role = serializers.SerializerMethodField()
    role_enum = serializers.CharField(write_only=True, required=False, help_text="Nombre del rol (marketing, asesor, staff, cliente)")
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'role_enum', 'date_joined']
        extra_kwargs = {'password': {'write_only': True}}

    def get_role(self, obj):
        """
        Método seguro para obtener el nombre del rol.
        """
        try:
            return obj.role.name if obj.role else None
        except:
            return None

    def create(self, validated_data):
        """
        Sobrescribe el método create para asignar un rol predeterminado si no se proporciona.
        """
        role_enum = validated_data.pop('role_enum', None)
        role = None
        
        if role_enum:
            try:
                role = Role.objects.get(name=role_enum)
            except Role.DoesNotExist:
                raise serializers.ValidationError(f"El rol '{role_enum}' no existe.")
        else:
            # Si no se especifica un rol, asigna el rol predeterminado (cliente)
            role = Role.objects.get_or_create(name=Role.CLIENTE)[0]
        
        # Crea el usuario con el rol asignado
        user = User.objects.create_user(**validated_data, role=role)
        return user

    def update(self, instance, validated_data):
        """
        Sobrescribe el método update para manejar la asignación de rol por enum y actualización de contraseña.
        """
        role_enum = validated_data.pop('role_enum', None)
        password = validated_data.pop('password', None)
        
        # Manejar la actualización del rol
        if role_enum:
            try:
                role = Role.objects.get(name=role_enum)
                instance.role = role
            except Role.DoesNotExist:
                raise serializers.ValidationError(f"El rol '{role_enum}' no existe.")
        
        # Manejar la actualización de la contraseña
        if password:
            instance.set_password(password)
        
        # Actualizar los demás campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


