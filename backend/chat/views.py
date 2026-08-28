import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .forms import ChatQueryForm
from .serializers import ConversationSerializer, MessageSerializer, AskQuestionSerializer
from documents.models import Document
from rag.pipeline import run_rag_pipeline, generate_conversation_title

# ==================== Django HTML & AJAX Views ====================

@login_required
def chat_page_view(request, conversation_id=None):
    """
    Renders interactive RAG chat interface with conversation sidebar, message stream,
    source citations, and document picker.
    """
    user_conversations = Conversation.objects.filter(user=request.user)
    user_documents = Document.objects.filter(user=request.user, processing_status=Document.STATUS_COMPLETED)

    active_conversation = None
    messages_list = []

    if conversation_id:
        active_conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        messages_list = active_conversation.messages.all()
    elif user_conversations.exists():
        active_conversation = user_conversations.first()
        messages_list = active_conversation.messages.all()

    form = ChatQueryForm(initial={'conversation_id': active_conversation.id if active_conversation else None})

    context = {
        'conversations': user_conversations,
        'active_conversation': active_conversation,
        'chat_messages': messages_list,
        'documents': user_documents,
        'form': form,
    }
    return render(request, 'chat/index.html', context)


@login_required
def new_conversation_view(request):
    """
    Creates a new conversation session and redirects to chat.
    """
    conversation = Conversation.objects.create(
        user=request.user,
        title="New Chat"
    )
    return redirect('chat_conversation', conversation_id=conversation.id)


@login_required
def delete_conversation_view(request, conversation_id):
    """
    Deletes a conversation and its messages.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversation.delete()
    messages.success(request, "Conversation deleted.")
    return redirect('chat_page')


@login_required
@require_POST
def ask_question_ajax_view(request):
    """
    AJAX endpoint for web chat interface:
    1. Receives question & optional conversation_id/document_id
    2. Runs Groq + ChromaDB RAG pipeline
    3. Saves user & assistant messages
    4. Returns JSON response with markdown answer and rich source citations
    """
    try:
        data = json.loads(request.body) if request.body else request.POST
        question = data.get('question', '').strip()
        conversation_id = data.get('conversation_id')
        document_id = data.get('document_id')

        if not question:
            return JsonResponse({'success': False, 'error': 'Question cannot be empty.'}, status=400)

        # Get or create conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=request.user)
            except Conversation.DoesNotExist:
                conversation = Conversation.objects.create(
                    user=request.user,
                    title=generate_conversation_title(question)
                )
        else:
            conversation = Conversation.objects.create(
                user=request.user,
                title=generate_conversation_title(question)
            )

        # Update title if it was "New Chat"
        if conversation.title == "New Chat":
            conversation.title = generate_conversation_title(question)
            conversation.save(update_fields=['title'])

        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_USER,
            content=question
        )

        # History for multi-turn context
        chat_history = list(conversation.messages.all())

        # Execute Groq RAG Pipeline
        rag_res = run_rag_pipeline(
            user_id=request.user.id,
            question=question,
            chat_history=chat_history,
            document_id=int(document_id) if document_id else None
        )

        answer = rag_res.get('answer', '')
        sources = rag_res.get('sources', [])

        # Save assistant message
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_ASSISTANT,
            content=answer,
            sources=sources
        )

        conversation.save(update_fields=['updated_at'])

        from django.utils import timezone
        user_local_time = timezone.localtime(user_msg.created_at).strftime('%I:%M %p').lstrip('0')
        assistant_local_time = timezone.localtime(assistant_msg.created_at).strftime('%I:%M %p').lstrip('0')

        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'conversation_title': conversation.title,
            'user_message': {
                'id': user_msg.id,
                'content': user_msg.content,
                'created_at': user_local_time,
                'created_at_iso': user_msg.created_at.isoformat()
            },
            'assistant_message': {
                'id': assistant_msg.id,
                'content': assistant_msg.content,
                'sources': assistant_msg.sources,
                'created_at': assistant_local_time,
                'created_at_iso': assistant_msg.created_at.isoformat()
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def chat_query_stream_view(request):
    """
    Server-Sent Events (SSE) streaming endpoint for real-time word-by-word token generation.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required.'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        question = data.get('question', '').strip()
        conversation_id = data.get('conversation_id')
        document_id = data.get('document_id') or None

        if not question:
            return JsonResponse({'error': 'Question cannot be empty.'}, status=400)

        # Retrieve or create conversation instantly without blocking LLM call
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        else:
            auto_title = question.split('\n')[0][:45].strip()
            if len(question) > 45:
                auto_title += "..."
            conversation = Conversation.objects.create(user=request.user, title=auto_title or "New Conversation")

        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_USER,
            content=question
        )

        chat_history = list(conversation.messages.all())

        def event_stream():
            from rag.pipeline import stream_rag_pipeline
            full_response = []

            for token in stream_rag_pipeline(
                user_id=request.user.id,
                question=question,
                chat_history=chat_history,
                document_id=document_id
            ):
                full_response.append(token)
                yield f"data: {json.dumps({'token': token})}\n\n"

            # Stream finished - persist assistant message
            complete_text = "".join(full_response).strip()
            assistant_msg = Message.objects.create(
                conversation=conversation,
                role=Message.ROLE_ASSISTANT,
                content=complete_text,
                sources=[]
            )
            conversation.save(update_fields=['updated_at'])

            from django.utils import timezone
            local_time = timezone.localtime(assistant_msg.created_at).strftime('%I:%M %p').lstrip('0')

            yield f"data: {json.dumps({'done': True, 'conversation_id': conversation.id, 'conversation_title': conversation.title, 'created_at': local_time})}\n\n"

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== REST API Views ====================

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        conversation = self.get_object()
        conversation.delete()
        return Response({
            'success': True,
            'message': 'Conversation deleted successfully'
        }, status=status.HTTP_200_OK)


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        except Conversation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Conversation not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)

        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })


class AskQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid query data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data['question']
        conversation_id = serializer.validated_data.get('conversation_id')

        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=request.user)
            except Conversation.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Conversation not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            title = generate_conversation_title(question)
            conversation = Conversation.objects.create(
                user=request.user,
                title=title
            )

        user_msg = Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_USER,
            content=question
        )

        chat_history = list(conversation.messages.all())

        rag_res = run_rag_pipeline(
            user_id=request.user.id,
            question=question,
            chat_history=chat_history
        )

        answer = rag_res['answer']
        sources = rag_res['sources']

        assistant_msg = Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_ASSISTANT,
            content=answer,
            sources=sources
        )

        conversation.save(update_fields=['updated_at'])

        return Response({
            'success': True,
            'data': {
                'conversation_id': conversation.id,
                'conversation_title': conversation.title,
                'user_message': MessageSerializer(user_msg).data,
                'assistant_message': MessageSerializer(assistant_msg).data,
                'answer': answer,
                'sources': sources
            }
        }, status=status.HTTP_200_OK)
