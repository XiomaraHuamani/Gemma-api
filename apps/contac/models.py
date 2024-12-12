from django.db import models

class CpInversion(models.Model):
    nombre_apellidos = models.CharField(max_length=255)
    correo_electronico = models.EmailField()
    numero_telefono = models.CharField(max_length=15, blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)
    objetivo_inversion = models.CharField(max_length=50, choices=[
        ('comercial', 'Comercial'),
        ('inversion', 'Inversión'),
    ])
    mensaje = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_apellidos} - {self.correo_electronico} - {self.fecha_creacion}"
