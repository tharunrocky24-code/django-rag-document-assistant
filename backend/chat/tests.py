from django.test import TestCase
from django.contrib.auth.models import User
from chat.models import Conversation, Message
from chat.forms import ChatQueryForm

class ChatModelAndFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='chatuser', password='password123')

    def test_conversation_and_message_flow(self):
        conv = Conversation.objects.create(user=self.user, title="Deep Space Telemetry")
        self.assertEqual(conv.title, "Deep Space Telemetry")
        self.assertEqual(conv.messages.count(), 0)

        # User message
        user_msg = Message.objects.create(
            conversation=conv,
            role=Message.ROLE_USER,
            content="What is Project Nebula?"
        )
        self.assertEqual(user_msg.role, 'user')

        # Assistant message with sources
        sources = [{"document": "nebula_specs.txt", "page": "1", "snippet": "Telemetry platform..."}]
        ai_msg = Message.objects.create(
            conversation=conv,
            role=Message.ROLE_ASSISTANT,
            content="Project Nebula is a quantum telemetry platform.",
            sources=sources
        )
        self.assertEqual(ai_msg.role, 'assistant')
        self.assertEqual(len(ai_msg.sources), 1)
        self.assertEqual(conv.messages.count(), 2)

    def test_chat_query_form_validation(self):
        form = ChatQueryForm(data={'question': 'How does Helios-9 work?'})
        self.assertTrue(form.is_valid())

        empty_form = ChatQueryForm(data={'question': ''})
        self.assertFalse(empty_form.is_valid())

