from django.test import TestCase, Client
from django.urls import reverse
import json
import uuid


class ChatbotViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.session_id = str(uuid.uuid4())

    def test_index_view(self):
        """Test that the index view loads successfully and provides a session ID."""
        response = self.client.get(reverse('chatbot:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'session_id')

    def test_chat_without_session_id(self):
        """Test that chat endpoint requires session ID."""
        response = self.client.post(
            reverse('chatbot:chat'),
            data=json.dumps({'message': 'Hello'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('Session ID is required', data['error'])

    def test_chat_without_message(self):
        """Test that chat endpoint requires a message."""
        response = self.client.post(
            reverse('chatbot:chat'),
            data=json.dumps({'session_id': self.session_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('Message is required', data['error'])

    def test_chat_successful(self):
        """Test successful chat interaction."""
        response = self.client.post(
            reverse('chatbot:chat'),
            data=json.dumps({
                'message': 'Hello chatbot',
                'session_id': self.session_id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertIn('response', data)
        self.assertEqual(data['session_id'], self.session_id)
        self.assertEqual(data['message_count'], 2)  # user + bot message

    def test_chat_history_persistence(self):
        """Test that chat history is maintained across requests."""
        # Send first message
        self.client.post(
            reverse('chatbot:chat'),
            data=json.dumps({
                'message': 'First message',
                'session_id': self.session_id
            }),
            content_type='application/json'
        )
        
        # Send second message
        response = self.client.post(
            reverse('chatbot:chat'),
            data=json.dumps({
                'message': 'Second message',
                'session_id': self.session_id
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.content)
        self.assertEqual(data['message_count'], 4)  # 2 user + 2 bot messages

    def test_get_chat_history(self):
        """Test retrieving chat history."""
        # Send a message first
        self.client.post(
            reverse('chatbot:chat'),
            data=json.dumps({
                'message': 'Test message',
                'session_id': self.session_id
            }),
            content_type='application/json'
        )
        
        # Get chat history
        response = self.client.get(
            reverse('chatbot:get_chat_history'),
            {'session_id': self.session_id}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['chat_history']), 2)
        self.assertEqual(data['chat_history'][0]['role'], 'user')
        self.assertEqual(data['chat_history'][0]['content'], 'Test message')
        self.assertEqual(data['chat_history'][1]['role'], 'assistant')

    def test_clear_chat_history(self):
        """Test clearing chat history."""
        # Send a message first
        self.client.post(
            reverse('chatbot:chat'),
            data=json.dumps({
                'message': 'Test message',
                'session_id': self.session_id
            }),
            content_type='application/json'
        )
        
        # Clear chat history
        response = self.client.post(
            reverse('chatbot:clear_chat_history'),
            data=json.dumps({'session_id': self.session_id}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        
        # Verify history is cleared
        history_response = self.client.get(
            reverse('chatbot:get_chat_history'),
            {'session_id': self.session_id}
        )
        history_data = json.loads(history_response.content)
        self.assertEqual(len(history_data['chat_history']), 0)

    def test_get_all_sessions(self):
        """Test getting information about all sessions."""
        # Create some chat history
        self.client.post(
            reverse('chatbot:chat'),
            data=json.dumps({
                'message': 'Test message',
                'session_id': self.session_id
            }),
            content_type='application/json'
        )
        
        response = self.client.get(reverse('chatbot:get_all_sessions'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertGreaterEqual(data['active_sessions'], 1)
        self.assertIn(self.session_id, data['sessions'])
