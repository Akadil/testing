from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import uuid
from .models import UploadedFile


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


class FileUploadTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.session_id = str(uuid.uuid4())

    def test_upload_file_without_session_id(self):
        """Test that file upload requires session ID."""
        test_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        response = self.client.post(
            reverse('chatbot:upload_file'),
            {'file': test_file}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('Session ID is required', data['error'])

    def test_upload_file_without_file(self):
        """Test that file upload requires a file."""
        response = self.client.post(
            reverse('chatbot:upload_file'),
            {'session_id': self.session_id}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('No file provided', data['error'])

    def test_upload_file_successful(self):
        """Test successful file upload."""
        test_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        response = self.client.post(
            reverse('chatbot:upload_file'),
            {
                'file': test_file,
                'session_id': self.session_id
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['file_info']['filename'], 'test.txt')
        
        # Verify file was saved to database
        self.assertEqual(UploadedFile.objects.filter(session_id=self.session_id).count(), 1)

    def test_upload_file_too_large(self):
        """Test file upload size limit."""
        # Create a file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        test_file = SimpleUploadedFile("large.txt", large_content, content_type="text/plain")
        response = self.client.post(
            reverse('chatbot:upload_file'),
            {
                'file': test_file,
                'session_id': self.session_id
            }
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('exceeds 10MB limit', data['error'])

    def test_upload_file_invalid_type(self):
        """Test file upload with invalid file type."""
        test_file = SimpleUploadedFile("test.exe", b"executable", content_type="application/x-executable")
        response = self.client.post(
            reverse('chatbot:upload_file'),
            {
                'file': test_file,
                'session_id': self.session_id
            }
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('not allowed', data['error'])

    def test_list_files(self):
        """Test listing uploaded files for a session."""
        # Upload a file first
        test_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        self.client.post(
            reverse('chatbot:upload_file'),
            {
                'file': test_file,
                'session_id': self.session_id
            }
        )
        
        # List files
        response = self.client.get(
            reverse('chatbot:list_files'),
            {'session_id': self.session_id}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['files'][0]['filename'], 'test.txt')

    def test_delete_file(self):
        """Test deleting an uploaded file."""
        # Upload a file first
        test_file = SimpleUploadedFile("test.txt", b"test content", content_type="text/plain")
        upload_response = self.client.post(
            reverse('chatbot:upload_file'),
            {
                'file': test_file,
                'session_id': self.session_id
            }
        )
        file_id = json.loads(upload_response.content)['file_info']['id']
        
        # Delete the file
        response = self.client.post(
            reverse('chatbot:delete_file'),
            data=json.dumps({
                'file_id': file_id,
                'session_id': self.session_id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        
        # Verify file was deleted from database
        self.assertEqual(UploadedFile.objects.filter(id=file_id).count(), 0)
