from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from documents.models import Document
from chat.models import Conversation, Message

def home_view(request):
    if request.user.is_authenticated:
        return redirect('chat_page')
    return redirect('login_page')

@login_required
def dashboard_view(request):
    documents = Document.objects.filter(user=request.user)
    conversations = Conversation.objects.filter(user=request.user)
    total_messages = Message.objects.filter(conversation__user=request.user).count()

    total_docs = documents.count()
    completed_docs = documents.filter(processing_status=Document.STATUS_COMPLETED).count()
    total_chunks = sum(doc.chunk_count for doc in documents)
    recent_docs = documents.order_by('-uploaded_at')[:5]
    recent_chats = conversations.order_by('-updated_at')[:5]

    context = {
        'total_docs': total_docs,
        'completed_docs': completed_docs,
        'total_chunks': total_chunks,
        'total_chats': conversations.count(),
        'total_messages': total_messages,
        'recent_docs': recent_docs,
        'recent_chats': recent_chats,
    }
    return render(request, 'dashboard/index.html', context)
