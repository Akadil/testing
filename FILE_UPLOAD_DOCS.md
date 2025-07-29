# File Upload Feature Documentation

This document explains the file upload functionality added to the Django chatbot application.

## Overview

The chatbot now supports file uploads, allowing users to upload documents, images, and other files that are stored locally on the server. Files are organized by session ID and can be managed through the web interface.

## Supported File Types

- **Text files**: `.txt`, `.csv`, `.json`, `.md`
- **Documents**: `.pdf`, `.doc`, `.docx`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`

## File Size Limitations

- Maximum file size: **10MB**
- This limit is configurable in Django settings

## File Storage

### Local Storage Structure
```
media/
└── uploads/
    └── [session_id]/
        ├── [uuid1].txt
        ├── [uuid2].pdf
        └── [uuid3].jpg
```

### Database Storage
Files are tracked in the `UploadedFile` model with the following information:
- Session ID
- Original filename
- File path
- File size
- Content type
- Upload timestamp

## API Endpoints

### 1. Upload File (`/chatbot/upload/`)
- **Method**: POST (multipart/form-data)
- **Parameters**:
  - `file`: The file to upload
  - `session_id`: The session identifier
- **Response**: File information including ID, filename, size, type, and URL

### 2. List Files (`/chatbot/files/`)
- **Method**: GET
- **Parameters**:
  - `session_id`: The session identifier (query parameter)
- **Response**: Array of all files uploaded in the session

### 3. Delete File (`/chatbot/delete-file/`)
- **Method**: POST
- **Parameters**:
  - `file_id`: The ID of the file to delete
  - `session_id`: The session identifier
- **Response**: Confirmation of deletion

## Frontend Features

### File Upload Interface
- **Attach File Button**: Allows users to select files
- **Drag & Drop**: (Can be added in future)
- **Progress Indicator**: Shows upload progress
- **File Validation**: Client-side validation for size and type

### File Management
- **File List**: Shows all uploaded files in the session
- **File Preview**: View/download files
- **File Deletion**: Remove files from the session
- **File Information**: Shows filename, size, and upload date

### Chat Integration
- Uploaded files appear as special messages in the chat
- File information is preserved in chat history
- Files can be referenced in conversations

## Implementation Details

### Django Model
```python
class UploadedFile(models.Model):
    session_id = models.CharField(max_length=100, db_index=True)
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to=upload_to_session_folder)
    file_size = models.BigIntegerField()
    content_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

### File Upload Function
```python
def upload_to_session_folder(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', instance.session_id, filename)
```

### Security Features
- File type validation (whitelist approach)
- File size limits
- UUID-based file naming (prevents conflicts)
- Session-based access control

## Usage Examples

### JavaScript File Upload
```javascript
const formData = new FormData();
formData.append('file', file);
formData.append('session_id', sessionId);

fetch('/chatbot/upload/', {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken') },
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.status === 'success') {
        console.log('File uploaded:', data.file_info);
    }
});
```

### Retrieving Files
```javascript
fetch(`/chatbot/files/?session_id=${sessionId}`)
.then(response => response.json())
.then(data => {
    console.log('Files:', data.files);
});
```

### Deleting Files
```javascript
fetch('/chatbot/delete-file/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        file_id: fileId,
        session_id: sessionId
    })
})
```

## Configuration

### Django Settings
```python
# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload limits
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644
```

### URL Configuration
```python
# In urls.py
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Testing

The implementation includes comprehensive tests:
- File upload validation
- File type restrictions
- File size limits
- File listing and deletion
- Session isolation
- Error handling

Run tests with:
```bash
python manage.py test chatbot.FileUploadTestCase
```

## Security Considerations

### Current Measures
1. **File Type Whitelist**: Only allowed file types can be uploaded
2. **Size Limits**: Prevents large file uploads that could fill disk space
3. **UUID Naming**: Prevents filename-based attacks
4. **Session Isolation**: Users can only access their own files

### Additional Recommendations for Production
1. **Virus Scanning**: Integrate with antivirus software
2. **File Content Validation**: Verify file contents match extensions
3. **Storage Quotas**: Limit total storage per user/session
4. **Cleanup Jobs**: Automatically delete old files
5. **CDN Integration**: Store files on external storage (AWS S3, etc.)

## Future Enhancements

### File Processing
- **Text Extraction**: Extract text from PDFs and documents for AI analysis
- **Image Analysis**: Use computer vision to analyze uploaded images
- **Document Parsing**: Parse structured documents (CSV, JSON)

### AI Integration
- **File Content Analysis**: Let ChatGPT analyze uploaded files
- **Context Integration**: Include file content in chat conversations
- **File Summarization**: Generate summaries of uploaded documents

### User Experience
- **Drag & Drop**: Add drag-and-drop file upload
- **Multiple Files**: Support uploading multiple files at once
- **File Thumbnails**: Show thumbnails for images
- **File Preview**: In-browser preview for common file types

### Storage & Performance
- **External Storage**: Integration with cloud storage services
- **File Compression**: Compress files to save space
- **Caching**: Cache file metadata for faster access
- **Background Processing**: Process large files asynchronously

## Admin Interface

Files can be managed through the Django admin interface:
- View all uploaded files
- Filter by content type and upload date
- Search by filename or session ID
- Monitor storage usage

Access at: `/admin/chatbot/uploadedfile/`

## Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file size (must be < 10MB)
   - Verify file type is allowed
   - Ensure media directory is writable

2. **Files Not Accessible**
   - Verify MEDIA_URL and MEDIA_ROOT settings
   - Check URL configuration includes static file serving
   - Ensure file permissions are correct

3. **Database Errors**
   - Run migrations: `python manage.py migrate`
   - Check database connection

### Debug Commands
```bash
# Check media directory permissions
ls -la media/uploads/

# View uploaded files in admin
python manage.py shell
>>> from chatbot.models import UploadedFile
>>> UploadedFile.objects.all()

# Clear test files
>>> UploadedFile.objects.filter(session_id='test-session').delete()
```
