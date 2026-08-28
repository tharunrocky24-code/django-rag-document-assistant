from django.urls import path
from .views import (
    chat_page_view,
    new_conversation_view,
    delete_conversation_view,
    ask_question_ajax_view,
    chat_query_stream_view
)

urlpatterns = [
    # HTML Chat views
    path('', chat_page_view, name='chat_page'),
    path('new/', new_conversation_view, name='chat_new'),
    path('<int:conversation_id>/', chat_page_view, name='chat_conversation'),
    path('<int:conversation_id>/delete/', delete_conversation_view, name='chat_delete'),
    path('query/ajax/', ask_question_ajax_view, name='chat_query_ajax'),
    path('query/stream/', chat_query_stream_view, name='chat_query_stream'),
]
