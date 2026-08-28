import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Sidebar } from '../components/Sidebar';
import { ChatMessage } from '../components/ChatMessage';
import { ChatInput } from '../components/ChatInput';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { chatService } from '../services/api';
import { Menu, MessageSquare, Bot, Sparkles } from 'lucide-react';

export const Chat = () => {
  const { conversationId } = useParams();
  const navigate = useNavigate();

  const [conversations, setConversations] = useState([]);
  const [messages, setMessages] = useState([]);
  const [activeConvId, setActiveConvId] = useState(conversationId ? parseInt(conversationId, 10) : null);
  const [loadingConversations, setLoadingConversations] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [asking, setAsking] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const res = await chatService.getConversations();
      const list = res.data.results || res.data || [];
      setConversations(list);
      return list;
    } catch (err) {
      console.error("Error loading conversations", err);
      return [];
    } finally {
      setLoadingConversations(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (conversationId) {
      const parsed = parseInt(conversationId, 10);
      setActiveConvId(parsed);
      loadMessages(parsed);
    } else {
      setActiveConvId(null);
      setMessages([]);
    }
  }, [conversationId]);

  const loadMessages = async (convId) => {
    setLoadingMessages(true);
    try {
      const res = await chatService.getMessages(convId);
      setMessages(res.data.data || res.data.results || res.data || []);
    } catch (err) {
      console.error("Failed to load messages", err);
    } finally {
      setLoadingMessages(false);
      setTimeout(scrollToBottom, 100);
    }
  };

  const handleSelectConversation = (id) => {
    navigate(`/chat/${id}`);
    setSidebarOpen(false);
  };

  const handleNewChat = () => {
    setActiveConvId(null);
    setMessages([]);
    navigate('/chat');
    setSidebarOpen(false);
  };

  const handleDeleteConversation = async (id) => {
    if (window.confirm("Are you sure you want to delete this conversation?")) {
      try {
        await chatService.deleteConversation(id);
        const updated = conversations.filter((c) => c.id !== id);
        setConversations(updated);
        if (activeConvId === id) {
          handleNewChat();
        }
      } catch (err) {
        alert("Failed to delete conversation.");
      }
    }
  };

  const handleSendMessage = async (question) => {
    // Optimistic user message append
    const tempUserMsg = {
      id: Date.now(),
      role: 'user',
      content: question,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setAsking(true);
    setTimeout(scrollToBottom, 50);

    try {
      const res = await chatService.askQuestion({
        conversation_id: activeConvId,
        question: question,
      });

      if (res.data.success) {
        const { conversation_id, conversation_title, assistant_message } = res.data.data;
        
        if (!activeConvId) {
          setActiveConvId(conversation_id);
          navigate(`/chat/${conversation_id}`, { replace: true });
          await fetchConversations();
        }

        setMessages((prev) => [...prev, assistant_message]);
      }
    } catch (err) {
      const errorMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: "Sorry, I encountered an error processing your query. Please check your document upload status or API key configuration.",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setAsking(false);
      setTimeout(scrollToBottom, 100);
    }
  };

  return (
    <div className="h-screen bg-slate-950 text-slate-100 flex flex-col overflow-hidden">
      <Navbar />

      <div className="flex-1 flex overflow-hidden relative">
        <Sidebar
          conversations={conversations}
          activeId={activeConvId}
          onSelectConversation={handleSelectConversation}
          onNewChat={handleNewChat}
          onDeleteConversation={handleDeleteConversation}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        {/* Main Chat Panel */}
        <div className="flex-1 flex flex-col h-full overflow-hidden bg-slate-950">
          {/* Header */}
          <div className="h-14 bg-slate-900/60 border-b border-slate-800 px-4 flex items-center justify-between shrink-0">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="md:hidden p-2 text-slate-400 hover:text-white rounded-lg"
              >
                <Menu className="w-5 h-5" />
              </button>
              <div className="flex items-center space-x-2">
                <Bot className="w-5 h-5 text-cyan-400" />
                <h2 className="font-semibold text-sm md:text-base text-slate-100 truncate">
                  {conversations.find((c) => c.id === activeConvId)?.title || 'AI Document Chat'}
                </h2>
              </div>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto space-y-2">
            {loadingMessages ? (
              <div className="h-full flex items-center justify-center">
                <LoadingSpinner size="lg" text="Loading messages..." />
              </div>
            ) : messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center p-8 text-center max-w-md mx-auto space-y-4">
                <div className="w-16 h-16 rounded-3xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                  <Sparkles className="w-8 h-8 text-cyan-400 animate-pulse" />
                </div>
                <h3 className="text-xl font-bold text-slate-100">Upload a document and ask a question</h3>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Our RAG pipeline will extract relevant facts only from your uploaded files and provide answers with page citations.
                </p>
              </div>
            ) : (
              messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
            )}

            {asking && (
              <div className="p-4 bg-slate-900/90 border-y border-slate-800/80">
                <LoadingSpinner size="sm" text="Retrieving context and generating AI response..." />
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input */}
          <ChatInput onSendMessage={handleSendMessage} disabled={asking} />
        </div>
      </div>
    </div>
  );
};
