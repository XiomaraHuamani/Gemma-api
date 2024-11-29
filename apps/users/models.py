from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from rest_framework_simplejwt.tokens import RefreshToken

AUTH_PROVIDERS = {
    'email': 'email',
    'google': 'google',
}


class Role(models.Model):
    """
    Modelo para definir roles en la aplicación.
    """
    MARKETING = 'marketing'
    ASESOR = 'asesor'
    STAFF = 'staff'
    CLIENTE = 'cliente'

    ROLE_CHOICES = [
        (MARKETING, 'Marketing'),
        (ASESOR, 'Asesor'),
        (STAFF, 'Staff'),
        (CLIENTE, 'Cliente'),
    ]

    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True,
        help_text="Tipo de rol asignado al usuario"
    )
    description = models.TextField(blank=True, null=True, help_text="Descripción del rol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de Creación"))

    class Meta:
        verbose_name = _("Rol")
        verbose_name_plural = _("Roles")

    def __str__(self):
        return dict(self.ROLE_CHOICES).get(self.name, self.name)


class User(AbstractUser):
    """
    Modelo personalizado de Usuario que utiliza un correo electrónico como username.
    """
    email = models.EmailField(
        max_length=255,
        verbose_name=_("Correo Electrónico"),
        unique=True
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número de teléfono debe estar en el formato: '+999999999'. Hasta 15 dígitos permitidos."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name=_("Número de Teléfono"),
        unique=True,
        null=True,
        blank=True
    )
    document_number = models.CharField(
        max_length=20,
        verbose_name=_("Número de Documento"),
        unique=True,
        null=True,
        blank=True
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_("Rol")
    )
    is_verified = models.BooleanField(default=False, verbose_name=_("Verificado"))
    auth_provider = models.CharField(
        max_length=50,
        default=AUTH_PROVIDERS.get('email'),
        verbose_name=_("Proveedor de Autenticación")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de Creación"))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone_number', 'document_number']

    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role.name if self.role else 'Sin Rol'})"

    @property
    def get_full_name(self):
        """
        Devuelve el nombre completo del usuario.
        """
        return f"{self.first_name.title()} {self.last_name.title()}"

    @property
    def tokens(self):
        """
        Genera los tokens de acceso y refresh para el usuario.
        """
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }

    def set_role(self, role_name):
        """
        Asigna un rol al usuario.
        """
        try:
            role = Role.objects.get(name=role_name)
            self.role = role
            self.save()
        except Role.DoesNotExist:
            raise ValueError(f"El rol '{role_name}' no existe.")


class OneTimePassword(models.Model):
    """
    Modelo para OTP (One-Time Password).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("Usuario"))
    otp = models.CharField(max_length=6, verbose_name=_("Código OTP"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Creado en"))

    def __str__(self):
        return f"OTP para {self.user.email}: {self.otp}"
