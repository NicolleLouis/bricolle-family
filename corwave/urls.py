from django.urls import path

from corwave.views.home import home, job_download, job_status

app_name = "corwave"

urlpatterns = [
    path("", home, name="home"),
    path("jobs/<int:job_id>/status", job_status, name="job_status"),
    path("jobs/<int:job_id>/download", job_download, name="job_download"),
]
