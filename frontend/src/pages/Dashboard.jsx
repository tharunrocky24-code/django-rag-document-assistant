import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { documentService, chatService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { FileText, MessageSquare, CheckCircle2, Plus, ArrowRight, Clock } from 'lucide-react';

export const Dashboard = () => {
  const { currentUser } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [docRes, chatRes] = await Promise.all([
          documentService.getDocuments(),
          chatService.getConversations(),
        ]);
        setDocuments(docRes.data.results || docRes.data || []);
        setConversations(chatRes.data.results || chatRes.data || []);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const processedCount = documents.filter((d) => d.processed || d.processing_status === 'completed').length;

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center">
          <LoadingSpinner size="lg" text="Loading Dashboard..." />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-8 space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 p-6 md:p-8 rounded-3xl border border-slate-800 shadow-xl">
          <div className="space-y-1">
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
              Welcome back, <span className="text-cyan-400">{currentUser?.username}</span> 👋
            </h1>
            <p className="text-sm text-slate-400">
              Query your uploaded documents and get instant AI answers with citations.
            </p>
          </div>

          <div className="flex items-center space-x-3 shrink-0">
            <Link
              to="/documents"
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold rounded-xl border border-slate-700 transition-colors flex items-center space-x-2"
            >
              <FileText className="w-4 h-4 text-blue-400" />
              <span>Upload Document</span>
            </Link>
            <Link
              to="/chat"
              className="px-4 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-sm font-semibold rounded-xl shadow-lg shadow-cyan-500/20 transition-all flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Start New Chat</span>
            </Link>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-lg flex items-center space-x-4">
            <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
              <FileText className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase text-slate-400">Total Documents</p>
              <p className="text-2xl font-bold text-slate-100">{documents.length}</p>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-lg flex items-center space-x-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase text-slate-400">Processed Documents</p>
              <p className="text-2xl font-bold text-slate-100">{processedCount}</p>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-lg flex items-center space-x-4">
            <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
              <MessageSquare className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase text-slate-400">Total Conversations</p>
              <p className="text-2xl font-bold text-slate-100">{conversations.length}</p>
            </div>
          </div>
        </div>

        {/* Recent Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Documents */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
                <FileText className="w-5 h-5 text-cyan-400" />
                <span>Recent Documents</span>
              </h2>
              <Link to="/documents" className="text-xs font-semibold text-cyan-400 hover:underline flex items-center space-x-1">
                <span>View all</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {documents.length === 0 ? (
              <div className="text-center py-10 bg-slate-950/50 rounded-2xl border border-slate-800/80 p-4">
                <p className="text-sm text-slate-400">No documents uploaded yet.</p>
                <Link to="/documents" className="mt-3 inline-block text-xs text-cyan-400 font-medium hover:underline">
                  Upload your first document →
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {documents.slice(0, 4).map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between bg-slate-950/50 p-4 rounded-xl border border-slate-800/80">
                    <div className="flex items-center space-x-3 truncate">
                      <FileText className="w-4 h-4 text-blue-400 shrink-0" />
                      <span className="text-sm font-medium text-slate-200 truncate">{doc.title}</span>
                    </div>
                    <span className="text-xs font-mono text-slate-500 uppercase">{doc.file_type}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Conversations */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
                <MessageSquare className="w-5 h-5 text-purple-400" />
                <span>Recent Conversations</span>
              </h2>
              <Link to="/chat" className="text-xs font-semibold text-cyan-400 hover:underline flex items-center space-x-1">
                <span>Open Chat</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {conversations.length === 0 ? (
              <div className="text-center py-10 bg-slate-950/50 rounded-2xl border border-slate-800/80 p-4">
                <p className="text-sm text-slate-400">No conversations yet.</p>
                <Link to="/chat" className="mt-3 inline-block text-xs text-cyan-400 font-medium hover:underline">
                  Start a new conversation →
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {conversations.slice(0, 4).map((conv) => (
                  <Link
                    key={conv.id}
                    to={`/chat/${conv.id}`}
                    className="flex items-center justify-between bg-slate-950/50 p-4 rounded-xl border border-slate-800/80 hover:border-cyan-500/40 transition-colors group"
                  >
                    <div className="flex items-center space-x-3 truncate">
                      <MessageSquare className="w-4 h-4 text-purple-400 shrink-0 group-hover:text-cyan-400" />
                      <span className="text-sm font-medium text-slate-200 truncate group-hover:text-cyan-400">{conv.title}</span>
                    </div>
                    <div className="flex items-center space-x-1 text-xs text-slate-500">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{new Date(conv.updated_at).toLocaleDateString()}</span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};
