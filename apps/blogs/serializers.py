from rest_framework import serializers
from .models import Blog

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            'id',
            'slug',
            'uniqueId',
            'titulo',
            'descripcion',
            'contenido',
            'autor',
            'categoria_nombre',
            'img1',
            'img2',
            'img3',
            'created_at',
            'updated_at',
        ]
