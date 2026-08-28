import React from 'react';
import { Bot, User, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex space-x-4 p-4 md:p-6 ${isUser ? 'bg-slate-900/40' : 'bg-slate-900/90 border-y border-slate-800/80'}`}>
      <div
        className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-md ${
          isUser
            ? 'bg-slate-800 text-slate-300 border border-slate-700'
            : 'bg-gradient-to-tr from-cyan-500 to-blue-600 text-white shadow-cyan-500/20'
        }`}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      <div className="flex-1 space-y-3 overflow-hidden">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            {isUser ? 'You' : 'DocuRAG AI'}
          </span>
          <span className="text-[10px] text-slate-500">
            {message.created_at ? new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
          </span>
        </div>

        <div className="prose prose-invert max-w-none text-slate-200 text-sm md:text-base leading-relaxed space-y-2">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-4 pt-3 border-t border-slate-800/80">
            <div className="text-xs font-semibold text-cyan-400 flex items-center space-x-1.5 mb-2">
              <FileText className="w-3.5 h-3.5" />
              <span>Source References</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {message.sources.map((src, i) => (
                <div
                  key={i}
                  className="inline-flex items-center space-x-1.5 bg-slate-800/80 hover:bg-slate-800 border border-slate-700/60 rounded-md px-2.5 py-1 text-xs text-slate-300 transition-colors"
                >
                  <span className="font-medium text-slate-200">📄 {src.document}</span>
                  {src.page && <span className="text-cyan-400 font-mono">Page {src.page}</span>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
