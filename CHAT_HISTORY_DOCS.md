# Chat History Implementation

This document explains how the chat history functionality is implemented in the Django chatbot application.

## Overview

The chatbot now maintains conversation history using an in-memory dictionary that stores chat sessions. Each session is identified by a unique session ID, and all messages (both user and assistant) are stored in chronological order.

## Architecture

### Data Structure

```python
CHAT_SESSIONS = {
    "session_id_1": [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How can I help you?"},
        {"role": "user", "content": "What's the weather like?"},
        {"role": "assistant", "content": "I don't have access to real-time weather data..."}
    ],
    "session_id_2": [
        {"role": "user", "content": "Different conversation"},
        {"role": "assistant", "content": "This is a separate session"}
    ]
}
```

### Session Management

1. **Session Creation**: When a user visits the chatbot page, a new UUID is generated as the session ID
2. **Session Storage**: Chat messages are stored in memory with the session ID as the key
3. **Context Preservation**: For OpenAI API calls, the entire chat history is sent as context

## API Endpoints

### 1. Chat Endpoint (`/chatbot/chat/`)
- **Method**: POST
- **Purpose**: Send messages and receive AI responses
- **Required Parameters**:
  - `message`: The user's message
  - `session_id`: The session identifier
- **Response**: Includes AI response, session ID, and message count

### 2. Get Chat History (`/chatbot/history/`)
- **Method**: GET
- **Purpose**: Retrieve chat history for a session
- **Parameters**:
  - `session_id`: The session identifier (query parameter)
- **Response**: Returns the complete chat history

### 3. Clear Chat History (`/chatbot/clear/`)
- **Method**: POST
- **Purpose**: Clear chat history for a session
- **Required Parameters**:
  - `session_id`: The session identifier
- **Response**: Confirmation of history clearing

### 4. Get All Sessions (`/chatbot/sessions/`)
- **Method**: GET
- **Purpose**: Get information about all active sessions (debugging)
- **Response**: List of active sessions with message counts

## Frontend Integration

The HTML template has been updated to:

1. **Display Session ID**: Shows a truncated version of the session ID in the chat header
2. **Send Session ID**: Includes the session ID in all API requests
3. **Clear Chat Button**: Allows users to clear their chat history
4. **Session Persistence**: Maintains the session throughout the page lifetime

## Usage Examples

### Basic Chat Flow

1. User visits `/chatbot/`
2. System generates session ID: `550e8400-e29b-41d4-a716-446655440000`
3. User sends message: "Hello"
4. System stores: `{"role": "user", "content": "Hello"}`
5. AI responds: "Hi there!"
6. System stores: `{"role": "assistant", "content": "Hi there!"}`
7. Subsequent messages build on this history

### API Usage

```javascript
// Send a chat message
fetch('/chatbot/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: "What did I ask about earlier?",
        session_id: "550e8400-e29b-41d4-a716-446655440000"
    })
})

// Get chat history
fetch('/chatbot/history/?session_id=550e8400-e29b-41d4-a716-446655440000')

// Clear chat history
fetch('/chatbot/clear/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        session_id: "550e8400-e29b-41d4-a716-446655440000"
    })
})
```

## Important Notes

### Memory Usage
- **In-Memory Storage**: Chat sessions are stored in server memory
- **Server Restart**: All chat history is lost when the server restarts
- **Memory Growth**: Long conversations and many sessions will increase memory usage

### Session Isolation
- Each session is completely isolated from others
- Multiple users can chat simultaneously without interference
- Session IDs are UUIDs, making them practically impossible to guess

### OpenAI Integration
- When OpenAI API key is configured, the full chat history is sent as context
- This allows ChatGPT to maintain conversation continuity
- The API call format follows OpenAI's chat completions format

## Testing

The implementation includes comprehensive tests:

- Session ID validation
- Message requirement validation
- Chat history persistence
- History retrieval
- History clearing
- Multi-session handling

Run tests with:
```bash
python manage.py test chatbot
```

## Future Enhancements

Consider these improvements for production use:

1. **Persistent Storage**: Use Django models to store chat history in the database
2. **Session Expiration**: Implement automatic cleanup of old sessions
3. **User Authentication**: Link sessions to authenticated users
4. **Memory Limits**: Set maximum message limits per session
5. **Redis Cache**: Use Redis for scalable session storage
6. **Session Recovery**: Allow users to resume conversations after server restarts
