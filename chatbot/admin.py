from django.contrib import admin
from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'session_id', 'file_size_formatted', 'content_type', 'uploaded_at']
    list_filter = ['content_type', 'uploaded_at']
    search_fields = ['original_filename', 'session_id']
    readonly_fields = ['file_size_formatted', 'uploaded_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-uploaded_at')
