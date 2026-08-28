from django.db import models
from django.contrib.auth.models import User
import os

def user_directory_path(instance, filename):
    return f'documents/user_{instance.user.id}/{filename}'

class Document(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=user_directory_path)
    file_type = models.CharField(max_length=10) # pdf, docx, txt
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    processing_error = models.TextField(blank=True, null=True)
    chunk_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def delete(self, *args, **kwargs):
        # Clean up storage file on model deletion
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)
