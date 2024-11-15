from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('locales/', include('apps.locales.urls')),  # Incluye las URLs de la aplicación locales
]
