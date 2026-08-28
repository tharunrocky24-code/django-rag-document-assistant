from django.test import TestCase
from django.contrib.auth.models import User
from documents.models import Document
from documents.forms import DocumentUploadForm
from django.core.files.uploadedfile import SimpleUploadedFile

class DocumentModelAndFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='docuser', password='password123')

    def test_document_creation(self):
        doc_file = SimpleUploadedFile("test_doc.txt", b"Hello ChromaDB RAG World", content_type="text/plain")
        doc = Document.objects.create(
            user=self.user,
            title="Test Doc",
            file=doc_file,
            file_type="txt",
            file_size=len(b"Hello ChromaDB RAG World"),
            processing_status=Document.STATUS_COMPLETED,
            chunk_count=1
        )
        self.assertEqual(doc.title, "Test Doc")
        self.assertEqual(doc.user.username, "docuser")
        self.assertEqual(doc.chunk_count, 1)

    def test_document_upload_form_valid(self):
        doc_file = SimpleUploadedFile("guide.pdf", b"%PDF-1.4 dummy pdf content", content_type="application/pdf")
        form = DocumentUploadForm(data={'title': 'My Guide'}, files={'file': doc_file})
        self.assertTrue(form.is_valid())

    def test_document_upload_form_invalid_extension(self):
        doc_file = SimpleUploadedFile("malicious.exe", b"binary data", content_type="application/octet-stream")
        form = DocumentUploadForm(data={'title': 'Exe file'}, files={'file': doc_file})
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)
