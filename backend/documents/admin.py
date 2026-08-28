from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'file_type', 'file_size', 'processing_status', 'processed', 'chunk_count', 'uploaded_at')
    list_filter = ('file_type', 'processing_status', 'processed')
    search_fields = ('title', 'user__username', 'user__email')
    readonly_fields = ('uploaded_at', 'chunk_count')
