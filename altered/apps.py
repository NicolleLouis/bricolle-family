from django.apps import AppConfig


class AlteredConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'altered'
