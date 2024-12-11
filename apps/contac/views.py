from rest_framework import generics
from django.core.mail import send_mail
from django.conf import settings
from .models import CpInversion
from .serializers import CpInversionSerializer


# Función para limpiar caracteres problemáticos
def clean_text(data):
    """Limpia caracteres problemáticos como espacios no rompibles."""
    if data:
        return data.replace('\xa0', ' ').strip()
    return data

class CpInversionListCreateView(generics.ListCreateAPIView):
    queryset = CpInversion.objects.all()
    serializer_class = CpInversionSerializer

    def perform_create(self, serializer):
        # Guardar el registro en la base de datos
        instance = serializer.save()

        # Construir el mensaje del correo
        email_message = f"""
        Nuevo registro recibido desde el formulario:

        Nombre y Apellidos: {instance.nombre_apellidos}
        Correo Electrónico: {instance.correo_electronico}
        Número de Teléfono: {instance.numero_telefono or "No proporcionado"}
        DNI: {instance.dni or "No proporcionado"}
        Tipo de Local: {instance.tipo_local}
        Objetivo de Inversión: {instance.objetivo_inversion}
        Mensaje: {instance.mensaje or "No proporcionado"}
        Fecha de Registro: {instance.fecha_creacion}

        Por favor, revisa esta información.
        """

        # Codificar el mensaje como UTF-8
        email_message = email_message.encode('utf-8').decode('utf-8')

        # Enviar el correo
        send_mail(
            subject="Nuevo registro de inversión",
            message=email_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
