from django.urls import path
from .views import (
    document_list_view,
    document_upload_view,
    document_delete_view,
    document_reprocess_view
)

urlpatterns = [
    # HTML Views
    path('', document_list_view, name='document_list'),
    path('upload/', document_upload_view, name='document_upload'),
    path('<int:pk>/delete/', document_delete_view, name='document_delete'),
    path('<int:pk>/reprocess/', document_reprocess_view, name='document_reprocess'),
]
