from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PrecioBase, Local

@receiver(post_save, sender=PrecioBase)
def update_local_prices(sender, instance, **kwargs):
    """
    Actualiza los precios de todos los locales al último precio base registrado.
    """
    Local.objects.all().update(precio=instance.precio)
