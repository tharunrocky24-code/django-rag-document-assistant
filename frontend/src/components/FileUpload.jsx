import React, { useState, useRef } from 'react';
import { UploadCloud, File, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

export const FileUpload = ({ onUploadSuccess }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const allowedTypes = ['.pdf', '.docx', '.txt'];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    setError(null);
    if (!selectedFile) return;

    const ext = '.' + selectedFile.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(ext)) {
      setError(`Unsupported file type '${ext}'. Please upload PDF, DOCX, or TXT.`);
      return;
    }

    if (selectedFile.size > 25 * 1024 * 1024) {
      setError('File exceeds maximum allowed size of 25MB.');
      return;
    }

    setFile(selectedFile);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setStatusText('Uploading file...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      setTimeout(() => {
        if (uploading) setStatusText('Processing document & generating vectors...');
      }, 1500);

      const res = await onUploadSuccess(formData);
      setStatusText('Document processed successfully!');
      setTimeout(() => {
        setFile(null);
        setUploading(false);
        setStatusText('');
      }, 1500);
    } catch (err) {
      setUploading(false);
      setStatusText('');
      setError(err.response?.data?.errors?.file?.[0] || err.response?.data?.message || 'Upload failed. Please try again.');
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
        <UploadCloud className="w-5 h-5 text-cyan-400" />
        <span>Upload Document</span>
      </h2>

      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all ${
          dragActive
            ? 'border-cyan-400 bg-cyan-500/10'
            : 'border-slate-800 hover:border-slate-700 bg-slate-950/50 hover:bg-slate-950'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleChange}
          className="hidden"
        />

        <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mb-3">
          <File className="w-6 h-6 text-cyan-400" />
        </div>

        <p className="text-sm font-medium text-slate-200">
          Click to browse or drag & drop files here
        </p>
        <p className="text-xs text-slate-500 mt-1">Supports PDF, DOCX, TXT (Max 25MB)</p>
      </div>

      {file && (
        <div className="flex items-center justify-between bg-slate-800/60 p-3.5 rounded-xl border border-slate-700/60">
          <div className="flex items-center space-x-3 truncate">
            <File className="w-5 h-5 text-cyan-400 shrink-0" />
            <span className="text-sm font-medium text-slate-200 truncate">{file.name}</span>
          </div>

          <button
            onClick={handleUpload}
            disabled={uploading}
            className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold rounded-lg text-xs md:text-sm shadow-md transition-all shrink-0 disabled:opacity-50"
          >
            {uploading ? 'Processing...' : 'Start Upload'}
          </button>
        </div>
      )}

      {statusText && (
        <div className="flex items-center space-x-2 text-xs font-medium text-cyan-400 bg-cyan-500/10 p-3 rounded-xl border border-cyan-500/20">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>{statusText}</span>
        </div>
      )}

      {error && (
        <div className="flex items-center space-x-2 text-xs font-medium text-rose-400 bg-rose-500/10 p-3 rounded-xl border border-rose-500/20">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
