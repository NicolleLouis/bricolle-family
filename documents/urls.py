from django.urls import path

from documents.views import (
    document_list,
    document_detail,
    DocumentCreateView,
    DocumentUpdateView,
)

app_name = "documents"

urlpatterns = [
    path("", document_list, name="document_list"),
    path("new/", DocumentCreateView.as_view(), name="document_create"),
    path("<int:pk>/", document_detail, name="document_detail"),
    path("<int:pk>/edit/", DocumentUpdateView.as_view(), name="document_edit"),
]
