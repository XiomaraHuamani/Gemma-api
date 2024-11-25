from django.db import models
from django.utils.text import slugify
import uuid

class Blog(models.Model):
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    uniqueId = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    titulo = models.CharField(max_length=255, help_text="Título del blog")
    descripcion = models.TextField(help_text="Descripción breve del blog")
    contenido = models.TextField(help_text="Contenido completo del blog")
    autor = models.CharField(max_length=100, help_text="Nombre del autor")
    categoria_nombre = models.CharField(max_length=100, help_text="Categoría asociada al blog")
    img1 = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    img2 = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    img3 = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Generar automáticamente el slug basado en el título si no existe
        if not self.slug:
            self.slug = slugify(self.titulo)
        super(Blog, self).save(*args, **kwargs)

    def __str__(self):
        return self.titulo
