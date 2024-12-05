# Generated by Django 4.2.16 on 2024-12-05 16:12

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('slug', models.SlugField(blank=True, max_length=255, unique=True)),
                ('uniqueId', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('titulo', models.TextField(help_text='Título del blog')),
                ('descripcion', models.TextField(help_text='Descripción breve del blog')),
                ('contenido', models.TextField(help_text='Contenido completo del blog')),
                ('autor', models.TextField(help_text='Nombre del autor')),
                ('categoria_nombre', models.TextField(help_text='Categoría asociada al blog')),
                ('img1', models.ImageField(blank=True, null=True, upload_to='blog_images/')),
                ('img2', models.ImageField(blank=True, null=True, upload_to='blog_images/')),
                ('img3', models.ImageField(blank=True, null=True, upload_to='blog_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
