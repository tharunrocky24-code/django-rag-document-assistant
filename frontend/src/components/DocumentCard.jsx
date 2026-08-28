import React from 'react';
import { FileText, Trash2, CheckCircle2, Clock, AlertCircle, Loader2 } from 'lucide-react';

export const DocumentCard = ({ document, onDelete }) => {
  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusBadge = (status, processed) => {
    if (processed || status === 'completed') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Completed</span>
        </span>
      );
    }
    if (status === 'processing') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          <span>Processing</span>
        </span>
      );
    }
    if (status === 'failed') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>Failed</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
        <Clock className="w-3.5 h-3.5" />
        <span>Pending</span>
      </span>
    );
  };

  return (
    <div className="bg-slate-900 border border-slate-800 hover:border-slate-700/80 rounded-2xl p-5 shadow-lg flex flex-col justify-between space-y-4 group transition-all">
      <div className="flex items-start justify-between space-x-3">
        <div className="flex items-center space-x-3 truncate">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shrink-0">
            <FileText className="w-5 h-5 text-blue-400" />
          </div>
          <div className="truncate">
            <h3 className="font-semibold text-slate-100 text-sm md:text-base truncate group-hover:text-cyan-400 transition-colors">
              {document.title}
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              {document.file_type?.toUpperCase()} • {formatBytes(document.file_size)}
            </p>
          </div>
        </div>
        <button
          onClick={() => onDelete(document.id)}
          className="p-2 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
          title="Delete Document"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 text-xs">
        <div>{getStatusBadge(document.processing_status, document.processed)}</div>
        <span className="text-slate-400">
          {document.chunk_count ? `${document.chunk_count} Chunks` : '0 Chunks'}
        </span>
      </div>

      {document.processing_error && (
        <p className="text-xs text-rose-400 bg-rose-500/10 p-2 rounded-lg border border-rose-500/20">
          {document.processing_error}
        </p>
      )}
    </div>
  );
};
