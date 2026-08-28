import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

export const ChatInput = ({ onSendMessage, disabled }) => {
  const [question, setQuestion] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [question]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim() && !disabled) {
      onSendMessage(question.trim());
      setQuestion('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-slate-900 border-t border-slate-800 relative">
      <div className="relative flex items-center bg-slate-950 border border-slate-800 rounded-2xl focus-within:border-cyan-500/60 focus-within:ring-1 focus-within:ring-cyan-500/30 transition-all shadow-inner">
        <textarea
          ref={textareaRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Ask a question about your uploaded documents... (Shift+Enter for newline)"
          rows={1}
          className="w-full bg-transparent text-slate-100 placeholder-slate-500 text-sm md:text-base px-4 py-3.5 pr-12 focus:outline-none resize-none min-h-[52px] max-h-[160px]"
        />
        <button
          type="submit"
          disabled={!question.trim() || disabled}
          className="absolute right-2.5 bottom-2.5 p-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white shadow-md transition-all"
        >
          {disabled ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
        </button>
      </div>
    </form>
  );
};
