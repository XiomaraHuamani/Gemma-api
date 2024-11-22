from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PrecioBase, Local

@receiver(post_save, sender=PrecioBase)
def update_local_prices(sender, instance, **kwargs):
    """
    Actualiza los precios en Local cuando se modifica un PrecioBase.
    """
    # Obtener los locales que coincidan con la zona y el metraje del PrecioBase
    locales_relacionados = Local.objects.filter(zona=instance.zona, metraje=instance.metraje)
    
    # Actualizar el precio de cada local
    for local in locales_relacionados:
        local.precio = instance.precio
        local.save()
