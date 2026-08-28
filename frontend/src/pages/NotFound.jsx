import React from 'react';
import { Link } from 'react-router-dom';
import { Bot, ArrowLeft } from 'lucide-react';

export const NotFound = () => {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 text-center space-y-4">
      <div className="w-16 h-16 rounded-3xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
        <Bot className="w-8 h-8 text-cyan-400" />
      </div>
      <h1 className="text-4xl font-bold text-slate-100">404 - Page Not Found</h1>
      <p className="text-slate-400 text-sm max-w-sm">The page you are looking for does not exist or has been moved.</p>
      <Link
        to="/dashboard"
        className="px-5 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold rounded-xl text-sm transition-all inline-flex items-center space-x-2"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Return to Dashboard</span>
      </Link>
    </div>
  );
};
