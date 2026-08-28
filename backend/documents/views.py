import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Document
from .forms import DocumentUploadForm
from .serializers import DocumentSerializer, DocumentUploadSerializer
from .services import process_document
from rag.vector_store import delete_document_vectors

# ==================== Django HTML Views ====================

@login_required
def document_list_view(request):
    """
    Renders user's uploaded documents with upload form and analytics.
    """
    documents = Document.objects.filter(user=request.user)
    form = DocumentUploadForm()

    # Document stats
    total_docs = documents.count()
    completed_docs = documents.filter(processing_status=Document.STATUS_COMPLETED).count()
    total_chunks = sum(doc.chunk_count for doc in documents)

    context = {
        'documents': documents,
        'form': form,
        'total_docs': total_docs,
        'completed_docs': completed_docs,
        'total_chunks': total_chunks,
    }
    return render(request, 'documents/list.html', context)


@login_required
def document_upload_view(request):
    """
    Handles document upload via Django Form and indexes into ChromaDB.
    """
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            title = form.cleaned_data.get('title') or uploaded_file.name
            ext = os.path.splitext(uploaded_file.name)[1].lower().strip('.')

            document = Document.objects.create(
                user=request.user,
                title=title,
                file=uploaded_file,
                file_type=ext,
                file_size=uploaded_file.size,
                processing_status=Document.STATUS_PENDING
            )

            # Ingest and vector index into ChromaDB
            success = process_document(document)

            if success:
                messages.success(request, f"'{document.title}' uploaded and indexed into ChromaDB successfully! ({document.chunk_count} chunks)")
            else:
                messages.warning(request, f"'{document.title}' uploaded, but processing encountered an error: {document.processing_error}")

            return redirect('document_list')
        else:
            messages.error(request, "Upload failed. Please check form errors.")
            documents = Document.objects.filter(user=request.user)
            return render(request, 'documents/list.html', {'documents': documents, 'form': form})

    return redirect('document_list')


@login_required
def document_delete_view(request, pk):
    """
    Deletes a document, its local file, and its ChromaDB vector embeddings.
    """
    document = get_object_or_404(Document, pk=pk, user=request.user)
    doc_title = document.title

    # Delete vectors from ChromaDB
    delete_document_vectors(user_id=request.user.id, document_id=document.id)

    # Delete Django model (also removes local storage file via model delete hook)
    document.delete()

    messages.success(request, f"Document '{doc_title}' and its vector embeddings were deleted.")
    return redirect('document_list')


@login_required
def document_reprocess_view(request, pk):
    """
    Re-processes and re-indexes an existing document into ChromaDB.
    """
    document = get_object_or_404(Document, pk=pk, user=request.user)
    
    # Clean previous vectors
    delete_document_vectors(user_id=request.user.id, document_id=document.id)

    # Reprocess
    success = process_document(document)
    if success:
        messages.success(request, f"'{document.title}' re-indexed successfully ({document.chunk_count} chunks).")
    else:
        messages.error(request, f"Re-indexing failed: {document.processing_error}")

    return redirect('document_list')


# ==================== REST API Views ====================

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        upload_serializer = DocumentUploadSerializer(data=request.data)
        if not upload_serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid file upload',
                'errors': upload_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = upload_serializer.validated_data['file']
        ext = os.path.splitext(uploaded_file.name)[1].lower().strip('.')

        document = Document.objects.create(
            user=request.user,
            title=uploaded_file.name,
            file=uploaded_file,
            file_type=ext,
            file_size=uploaded_file.size,
            processing_status=Document.STATUS_PENDING
        )

        process_document(document)
        serializer = DocumentSerializer(document)
        return Response({
            'success': True,
            'message': 'Document uploaded and processed successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        delete_document_vectors(user_id=request.user.id, document_id=document.id)
        document.delete()
        return Response({
            'success': True,
            'message': 'Document and vector embeddings deleted successfully'
        }, status=status.HTTP_200_OK)
