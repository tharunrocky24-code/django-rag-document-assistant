from django.urls import path, include
from rest_framework.routers import DefaultRouter
from documents.views import DocumentViewSet
from chat.views import ConversationViewSet, MessageListView, AskQuestionView
from accounts.views import RegisterView, LoginView, UserMeView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

doc_router = DefaultRouter()
doc_router.register(r'', DocumentViewSet, basename='api_document')

chat_router = DefaultRouter()
chat_router.register(r'', ConversationViewSet, basename='api_conversation')

urlpatterns = [
    # Auth API
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('auth/login/', LoginView.as_view(), name='api_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('auth/me/', UserMeView.as_view(), name='api_user_me'),
    path('auth/logout/', LogoutView.as_view(), name='api_logout'),

    # Documents API
    path('documents/', include(doc_router.urls)),

    # Chat & Conversations API
    path('conversations/', include(chat_router.urls)),
    path('conversations/<int:conversation_id>/messages/', MessageListView.as_view(), name='api_conversation_messages'),
    path('chat/ask/', AskQuestionView.as_view(), name='api_chat_ask'),
]
