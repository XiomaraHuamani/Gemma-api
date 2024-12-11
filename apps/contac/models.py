from django.db import models

# Create your models here.

class CpInversion(models.Model):
    nombre_apellidos = models.CharField(max_length=255)
    correo_electronico = models.EmailField()
    numero_telefono = models.CharField(max_length=15, blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)
    tipo_local = models.CharField(max_length=50, choices=[
        ('12.5', '12.5 m²'),
        ('25', '25 m²'),
        ('50', '50 m²'),
        ('300', '300 m²'),
    ])
    objetivo_inversion = models.CharField(max_length=50, choices=[
        ('comercial', 'Comercial'),
        ('inversion', 'Inversión'),
    ])
    mensaje = models.TextField(blank=True, null=True)
    acepta_terminos = models.BooleanField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Registra la fecha y hora de creación

    def __str__(self):
        return f"{self.nombre_apellidos} - {self.correo_electronico} - {self.fecha_creacion}"