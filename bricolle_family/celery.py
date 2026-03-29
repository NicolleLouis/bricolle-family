import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bricolle_family.settings")

app = Celery("bricolle_family")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
