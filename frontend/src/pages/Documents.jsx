import React, { useEffect, useState } from 'react';
import { Navbar } from '../components/Navbar';
import { FileUpload } from '../components/FileUpload';
import { DocumentCard } from '../components/DocumentCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { documentService } from '../services/api';
import { FileText } from 'lucide-react';

export const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDocuments = async () => {
    try {
      const res = await documentService.getDocuments();
      setDocuments(res.data.results || res.data || []);
    } catch (err) {
      console.error("Failed to fetch documents", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUploadSuccess = async (formData) => {
    const res = await documentService.uploadDocument(formData);
    await fetchDocuments();
    return res;
  };

  const handleDeleteDocument = async (id) => {
    if (window.confirm("Are you sure you want to delete this document and its vector search data?")) {
      try {
        await documentService.deleteDocument(id);
        setDocuments(documents.filter((doc) => doc.id !== id));
      } catch (err) {
        alert("Failed to delete document.");
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-8 space-y-8">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Document Management</h1>
          <p className="text-sm text-slate-400 mt-1">
            Upload PDF, DOCX, or TXT documents to power your AI RAG context.
          </p>
        </div>

        <FileUpload onUploadSuccess={handleUploadSuccess} />

        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
            <FileText className="w-5 h-5 text-blue-400" />
            <span>Your Uploaded Documents ({documents.length})</span>
          </h2>

          {loading ? (
            <LoadingSpinner size="md" text="Loading documents..." />
          ) : documents.length === 0 ? (
            <div className="text-center py-16 bg-slate-900 border border-slate-800 rounded-3xl p-8">
              <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-300 font-medium">No documents uploaded yet.</p>
              <p className="text-xs text-slate-500 mt-1">
                Upload your first PDF, DOCX or TXT document using the uploader above.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {documents.map((doc) => (
                <DocumentCard key={doc.id} document={doc} onDelete={handleDeleteDocument} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
