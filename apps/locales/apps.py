from django.apps import AppConfig

class LocalesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.locales'

    def ready(self):
        import apps.locales.signals  # Importar las señales
