from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Role, User
from .serializers import RoleSerializer, RoleCreateUpdateSerializer, UserSerializer, UserListSerializer
from rest_framework import status

class RoleViewSet(ModelViewSet):
    """
    ViewSet para gestionar los roles.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [AllowAny] 

    def get_serializer_class(self):
        """
        Usa diferentes serializers según la acción.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return RoleCreateUpdateSerializer
        return RoleSerializer

    def perform_create(self, serializer):
        """
        Lógica adicional al crear un rol.
        """
        serializer.save()

    def get_queryset(self):
        """
        Permite filtrar roles por valor de enum.
        """
        queryset = super().get_queryset()
        role_enum = self.request.query_params.get('role_enum', None)
        if role_enum:
            queryset = queryset.filter(name=role_enum)
        return queryset

    @action(detail=False, methods=['get'], url_path='por-enum/(?P<role_enum>[^/.]+)')
    def por_enum(self, request, role_enum=None):
        """
        Obtener un rol específico por su valor de enum.
        """
        try:
            role = Role.objects.get(name=role_enum)
            serializer = self.get_serializer(role)
            return Response(serializer.data)
        except Role.DoesNotExist:
            return Response(
                {"error": f"El rol '{role_enum}' no existe."}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def enums(self, request):
        """
        Obtener todos los valores de enum disponibles.
        """
        return Response({
            "enums": [
                {"valor": choice[0], "etiqueta": choice[1]} 
                for choice in Role.ROLE_CHOICES
            ]
        })

    @action(detail=False, methods=['post'])
    def crear_por_enum(self, request):
        """
        Crear un rol usando el enum value.
        """
        serializer = RoleCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            return Response({
                "mensaje": f"Rol '{role.name}' creado exitosamente.",
                "rol": RoleSerializer(role).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put', 'patch'], url_path='actualizar-por-enum/(?P<role_enum>[^/.]+)')
    def actualizar_por_enum(self, request, role_enum=None):
        """
        Actualizar un rol usando el enum value.
        """
        try:
            role = Role.objects.get(name=role_enum)
            serializer = RoleCreateUpdateSerializer(role, data=request.data, partial=True)
            if serializer.is_valid():
                updated_role = serializer.save()
                return Response({
                    "mensaje": f"Rol '{updated_role.name}' actualizado exitosamente.",
                    "rol": RoleSerializer(updated_role).data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Role.DoesNotExist:
            return Response(
                {"error": f"El rol '{role_enum}' no existe."}, 
                status=status.HTTP_404_NOT_FOUND
            )


class UserViewSet(ModelViewSet):
    """
    ViewSet para gestionar los usuarios.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  

    def get_serializer_class(self):
        """
        Usa diferentes serializers según la acción.
        """
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer

    def get_permissions(self):
        """
        Personalizar permisos para ciertas acciones.
        """
        if self.action in ['create', 'list']:
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        Permite filtrar usuarios por enum de rol.
        """
        try:
            queryset = super().get_queryset()
            role_enum = self.request.query_params.get('role_enum', None)
            if role_enum:
                queryset = queryset.filter(role__name=role_enum)
            return queryset
        except Exception as e:
            # Log del error para debugging
            print(f"Error en get_queryset: {str(e)}")
            return User.objects.none()

    def list(self, request, *args, **kwargs):
        """
        Sobrescribe el método list para mejor manejo de errores.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Error al obtener la lista de usuarios: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        """
        Método para personalizar el proceso de creación.
        """
        serializer.save()

    def perform_update(self, serializer):
        """
        Método para personalizar el proceso de actualización.
        """
        serializer.save()

    def perform_destroy(self, instance):
        """
        Método para personalizar la eliminación de usuarios.
        """
        instance.delete()

    @action(detail=False, methods=['get'], url_path='por-rol/(?P<role_enum>[^/.]+)')
    def por_rol(self, request, role_enum=None):
        """
        Obtener usuarios por enum de rol.
        """
        try:
            users = User.objects.filter(role__name=role_enum)
            serializer = UserListSerializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": f"Error al obtener usuarios con rol '{role_enum}': {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def me(self, request):
        """
        Obtén información del usuario autenticado.
        """
        try:
            if request.user.is_authenticated:
                serializer = self.get_serializer(request.user)
                return Response(serializer.data)
            else:
                return Response(
                    {"error": "Usuario no autenticado"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            return Response(
                {"error": f"Error al obtener información del usuario: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def asignar_rol(self, request, pk=None):
        """
        Asignar un rol específico a un usuario.
        """
        try:
            user = self.get_object()
            role_name = request.data.get('role_name')
            if not role_name:
                return Response({"error": "El campo 'role_name' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                role = Role.objects.get(name=role_name)
            except Role.DoesNotExist:
                return Response({"error": f"El rol '{role_name}' no existe."}, status=status.HTTP_404_NOT_FOUND)

            user.role = role
            user.save()
            return Response({"mensaje": f"Rol '{role_name}' asignado al usuario {user.email}."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error al asignar rol: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def cambiar_password(self, request, pk=None):
        """
        Cambiar la contraseña de un usuario.
        """
        try:
            user = self.get_object()
            nueva_password = request.data.get('nueva_password')
            password_actual = request.data.get('password_actual')
            
            if not nueva_password:
                return Response({"error": "El campo 'nueva_password' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Si se proporciona la contraseña actual, verificar que sea correcta
            if password_actual:
                if not user.check_password(password_actual):
                    return Response({"error": "La contraseña actual es incorrecta."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Cambiar la contraseña
            user.set_password(nueva_password)
            user.save()
            
            return Response({"mensaje": "Contraseña actualizada exitosamente."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error al cambiar contraseña: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def reset_password(self, request, pk=None):
        """
        Resetear la contraseña de un usuario (sin verificar contraseña actual).
        """
        try:
            user = self.get_object()
            nueva_password = request.data.get('nueva_password')
            
            if not nueva_password:
                return Response({"error": "El campo 'nueva_password' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Cambiar la contraseña
            user.set_password(nueva_password)
            user.save()
            
            return Response({"mensaje": "Contraseña reseteada exitosamente."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error al resetear contraseña: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegisterView(APIView):
    """
    Vista para el registro de usuarios.
    """
    permission_classes = [AllowAny]  

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)  
            return Response({
                "usuario": serializer.data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        
        # Agregar el rol del usuario a la respuesta
        data['rol'] = user.role.name if user.role else None
        # Agregar el username del usuario a la respuesta
        data['username'] = user.username
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

