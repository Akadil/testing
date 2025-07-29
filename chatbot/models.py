from django.db import models
import os
import uuid


def upload_to_session_folder(instance, filename):
    """Upload files to a folder based on session ID."""
    # Get file extension
    ext = filename.split('.')[-1]
    # Create new filename using UUID
    filename = f"{uuid.uuid4()}.{ext}"
    # Return the full path
    return os.path.join('uploads', instance.session_id, filename)


class UploadedFile(models.Model):
    """Model to store information about uploaded files."""
    session_id = models.CharField(max_length=100, db_index=True)
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to=upload_to_session_folder)
    file_size = models.BigIntegerField()  # Size in bytes
    content_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.original_filename} ({self.session_id[:8]}...)"
    
    @property
    def file_size_formatted(self):
        """Return human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @property
    def file_url(self):
        """Return the URL to access the file."""
        return self.file.url if self.file else None
