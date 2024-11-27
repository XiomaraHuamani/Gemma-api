from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Role, User
from .serializers import RoleSerializer, UserSerializer
from rest_framework import status

class RoleViewSet(ModelViewSet):
    """
    ViewSet para gestionar los roles.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [AllowAny] 

    def perform_create(self, serializer):
        """
        Lógica adicional al crear un rol.
        """
        serializer.save()


class UserViewSet(ModelViewSet):
    """
    ViewSet para gestionar los usuarios.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  

    def get_permissions(self):
        """
        Personalizar permisos para ciertas acciones.
        """
        if self.action in ['create', 'list']:
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    
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
        Método para personalizar la eliminación de roles.
        """
        instance.delete()

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def me(self, request):
        """
        Obtén información del usuario autenticado.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def set_role(self, request, pk=None):
        """
        Asignar un rol específico a un usuario.
        """
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
        return Response({"message": f"Rol '{role_name}' asignado al usuario {user.email}."}, status=status.HTTP_200_OK)


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
                "user": serializer.data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint personalizado para obtener tokens JWT.
    Incluye el rol del usuario en la respuesta.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # Si el token se genera correctamente, agrega el rol
        if response.status_code == 200:
            try:
                # Recuperar el usuario autenticado por el email
                user = User.objects.get(email=request.data.get('email'))

                # Agregar el rol a la respuesta
                response.data['role'] = user.role.name if user.role else "No Role Assigned"
            except User.DoesNotExist:
                response.data['role'] = "No Role Found"
        return response

