from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('locales/', include('apps.locales.urls')), 
    path('blogs/', include('apps.blogs.urls')), 
    path('users/', include('apps.users.urls')),
    path('contac/', include('apps.contac.urls')),

]

if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 