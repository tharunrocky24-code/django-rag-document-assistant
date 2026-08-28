import os
from django import forms
from .models import Document

ALLOWED_EXTENSIONS = ['pdf', 'docx', 'txt', 'md', 'csv']
MAX_FILE_SIZE_MB = 25

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file', 'title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Optional custom title (defaults to filename)'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': '.pdf,.docx,.txt,.md,.csv'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise forms.ValidationError("No file selected.")

        # Check extension
        ext = os.path.splitext(file.name)[1].lower().strip('.')
        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                f"Unsupported file format '.{ext}'. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Check size (25MB limit)
        if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise forms.ValidationError(f"File size exceeds the {MAX_FILE_SIZE_MB}MB limit.")

        return file
