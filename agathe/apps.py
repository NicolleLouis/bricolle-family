from django.apps import AppConfig


class AgatheConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agathe'

    def ready(self):
        import agathe.signals  # noqa: F401
