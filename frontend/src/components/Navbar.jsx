import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Bot, LogOut, FileText, MessageSquare, LayoutDashboard, User } from 'lucide-react';

export const Navbar = () => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-40">
      <Link to="/dashboard" className="flex items-center space-x-3 group">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
          <Bot className="w-6 h-6 text-white" />
        </div>
        <span className="font-bold text-lg text-slate-100 tracking-tight">
          Docu<span className="text-cyan-400">RAG</span> AI
        </span>
      </Link>

      <nav className="flex items-center space-x-1 sm:space-x-4">
        <Link
          to="/dashboard"
          className="px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors flex items-center space-x-2"
        >
          <LayoutDashboard className="w-4 h-4 text-cyan-400" />
          <span className="hidden sm:inline">Dashboard</span>
        </Link>
        <Link
          to="/documents"
          className="px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors flex items-center space-x-2"
        >
          <FileText className="w-4 h-4 text-blue-400" />
          <span className="hidden sm:inline">Documents</span>
        </Link>
        <Link
          to="/chat"
          className="px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors flex items-center space-x-2"
        >
          <MessageSquare className="w-4 h-4 text-purple-400" />
          <span className="hidden sm:inline">Chat</span>
        </Link>

        {currentUser && (
          <div className="flex items-center space-x-3 pl-4 border-l border-slate-800">
            <div className="flex items-center space-x-2 bg-slate-800/50 px-3 py-1.5 rounded-full border border-slate-700/50">
              <User className="w-4 h-4 text-slate-400" />
              <span className="text-xs font-semibold text-slate-200">{currentUser.username}</span>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        )}
      </nav>
    </header>
  );
};
