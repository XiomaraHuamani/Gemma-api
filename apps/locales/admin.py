from django.contrib import admin
from .models import (
    Zona, Categoria, TipoDescuento, Descuento, Local, 
    ReciboArras, Cliente, TipoVenta, VentaCredito, 
    VentaContado, Pago, Galeria
)

# Register your models here.

@admin.register(Galeria)
class GaleriaAdmin(admin.ModelAdmin):
    list_display = ['name', 'files']
    search_fields = ['name']
    ordering = ['name']


# Registrar otros modelos existentes
admin.site.register(Zona)
admin.site.register(Categoria)
admin.site.register(TipoDescuento)
admin.site.register(Descuento)
admin.site.register(Local)
admin.site.register(ReciboArras)
admin.site.register(Cliente)
admin.site.register(TipoVenta)
admin.site.register(VentaCredito)
admin.site.register(VentaContado)
admin.site.register(Pago)
