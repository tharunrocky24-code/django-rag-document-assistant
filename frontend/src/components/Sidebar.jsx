import React from 'react';
import { Plus, MessageSquare, Trash2, FileText, Settings, X } from 'lucide-react';

export const Sidebar = ({
  conversations = [],
  activeId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  isOpen,
  onClose
}) => {
  return (
    <aside
      className={`fixed md:static inset-y-0 left-0 z-30 w-72 bg-slate-900 border-r border-slate-800 flex flex-col transition-transform duration-300 transform ${
        isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      }`}
    >
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium py-2.5 px-4 rounded-xl shadow-lg shadow-cyan-500/20 transition-all"
        >
          <Plus className="w-5 h-5" />
          <span>New Chat</span>
        </button>
        {onClose && (
          <button onClick={onClose} className="md:hidden ml-2 text-slate-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        <div className="px-3 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Conversations
        </div>
        {conversations.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">No conversations yet</div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => onSelectConversation(conv.id)}
              className={`group flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer text-sm font-medium transition-colors ${
                activeId === conv.id
                  ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                  : 'text-slate-300 hover:bg-slate-800/50 hover:text-white'
              }`}
            >
              <div className="flex items-center space-x-3 truncate">
                <MessageSquare className="w-4 h-4 shrink-0 text-slate-400 group-hover:text-cyan-400" />
                <span className="truncate">{conv.title || 'Untitled Chat'}</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteConversation(conv.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-all"
                title="Delete Conversation"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  );
};
