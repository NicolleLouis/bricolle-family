from django.urls import path

from games_collection.views.home import home
from games_collection.views.back_to_the_dawn import back_to_the_dawn
from games_collection.views.markdown_document import (
    markdown_document_list,
    MarkdownDocumentCreateView,
    MarkdownDocumentUpdateView,
)

app_name = 'games_collection'

urlpatterns = [
    path('', home, name='home'),
    path('back_to_the_dawn/', back_to_the_dawn, name='back_to_the_dawn'),
    path('docs/', markdown_document_list, name='markdown_document_list'),
    path('docs/new/', MarkdownDocumentCreateView.as_view(), name='markdown_document_create'),
    path('docs/<int:pk>/edit/', MarkdownDocumentUpdateView.as_view(), name='markdown_document_edit'),
]
