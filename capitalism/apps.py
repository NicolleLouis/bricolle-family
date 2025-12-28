from django.apps import AppConfig


class CapitalismConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "capitalism"
    verbose_name = "Capitalism"

    def ready(self):
        from capitalism import signals

        signals.connect_signals()
