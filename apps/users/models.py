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
        return self.get_name_display()


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
        null=True,  # Temporalmente permitimos null
        blank=True  # Temporalmente permitimos blank
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
        # Si el nombre de usuario no está definido, usar el correo electrónico como username.
        if not self.username:
            self.username = self.email
        super(User, self).save(*args, **kwargs)

    @property
    def get_full_name(self):
        """Devuelve el nombre completo del usuario."""
        return f"{self.first_name.title()} {self.last_name.title()}"

    @property
    def is_marketing(self):
        """Verifica si el usuario pertenece al rol de marketing."""
        return self.role and self.role.name == Role.MARKETING

    @property
    def is_asesor(self):
        """Verifica si el usuario pertenece al rol de asesor."""
        return self.role and self.role.name == Role.ASESOR

    @property
    def is_staff_member(self):
        """Verifica si el usuario pertenece al rol de staff."""
        return self.role and self.role.name == Role.STAFF

    @property
    def is_cliente(self):
        """Verifica si el usuario pertenece al rol de cliente."""
        return self.role and self.role.name == Role.CLIENTE

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
        valid_roles = [role[0] for role in Role.ROLE_CHOICES]
        if role_name not in valid_roles:
            raise ValueError(f"Rol inválido. Los roles válidos son: {', '.join(valid_roles)}.")
        role, _ = Role.objects.get_or_create(name=role_name)
        self.role = role
        self.save()


class OneTimePassword(models.Model):
    """
    Modelo para OTP (One-Time Password).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("Usuario"))
    otp = models.CharField(max_length=6, verbose_name=_("Código OTP"))

    def __str__(self):
        return f"OTP para {self.user.get_full_name}: {self.otp}"
