from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    uploaded_at = serializers.DateTimeField(read_only=True)
    processed = serializers.BooleanField(read_only=True)
    processing_status = serializers.CharField(read_only=True)
    processing_error = serializers.CharField(read_only=True)
    chunk_count = serializers.IntegerField(read_only=True)
    file_size = serializers.IntegerField(read_only=True)
    file_type = serializers.CharField(read_only=True)

    class Meta:
        model = Document
        fields = ('id', 'title', 'file', 'file_type', 'file_size', 'uploaded_at', 'processed', 'processing_status', 'processing_error', 'chunk_count')
        read_only_fields = ('id', 'user')

class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate_file(self, value):
        valid_extensions = ['.pdf', '.docx', '.txt']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError(f"Unsupported file format '{ext}'. Allowed formats: PDF, DOCX, TXT.")
        
        # Max file size 25MB
        if value.size > 25 * 1024 * 1024:
            raise serializers.ValidationError("File size exceeds 25MB limit.")
            
        return value
