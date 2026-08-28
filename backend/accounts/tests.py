from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from documents.models import Document
from chat.models import Conversation, Message
from rag.retriever import retrieve_user_chunks
from rag.vector_store import add_chunks_to_vector_store
from langchain_core.documents import Document as LCDocument

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'

    def test_user_registration(self):
        data = {
            'username': 'testuser1',
            'email': 'testuser1@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser1').exists())

    def test_user_login(self):
        User.objects.create_user(username='loginuser', email='login@example.com', password='Password123!')
        response = self.client.post(self.login_url, {'username': 'loginuser', 'password': 'Password123!'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])

class UserIsolationAndRAGTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='usera', password='Password123!')
        self.user_b = User.objects.create_user(username='userb', password='Password123!')
        
        self.client_a = APIClient()
        self.client_a.force_authenticate(user=self.user_a)
        
        self.client_b = APIClient()
        self.client_b.force_authenticate(user=self.user_b)

    def test_document_isolation(self):
        # User A uploads doc A
        doc_a = Document.objects.create(
            user=self.user_a,
            title='User A Confidential.pdf',
            file_type='pdf',
            file_size=1024,
            processing_status='completed'
        )

        # User B fetches documents list
        res_b = self.client_b.get('/api/documents/')
        self.assertEqual(res_b.status_code, status.HTTP_200_OK)
        doc_ids = [d['id'] for d in res_b.data]
        self.assertNotIn(doc_a.id, doc_ids)

        # User B attempts to access Document A directly
        res_b_detail = self.client_b.get(f'/api/documents/{doc_a.id}/')
        self.assertEqual(res_b_detail.status_code, status.HTTP_404_NOT_FOUND)

    def test_conversation_isolation(self):
        conv_a = Conversation.objects.create(user=self.user_a, title='User A Secret Chat')

        # User B attempts to get messages of User A's conversation
        res_b = self.client_b.get(f'/api/conversations/{conv_a.id}/messages/')
        self.assertEqual(res_b.status_code, status.HTTP_404_NOT_FOUND)

    def test_vector_user_isolation(self):
        # Mock vector store insertion for User A
        chunks_a = [LCDocument(page_content="Secret formula for User A.", metadata={})]
        add_chunks_to_vector_store(chunks_a, user_id=self.user_a.id, document_id=999, document_name="UserA.pdf")

        # Query for User B
        retrieved_b = retrieve_user_chunks(query="Secret formula", user_id=self.user_b.id)
        # Verify User B receives ZERO chunks from User A
        for chunk in retrieved_b:
            self.assertNotEqual(chunk.metadata.get('user_id'), str(self.user_a.id))
