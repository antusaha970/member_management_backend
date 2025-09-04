# core/middleware.py
import json
from django.conf import settings
from django.http import JsonResponse

class MaxUploadSizeMiddleware:
    """
    Reject request if total body size exceeds DATA_UPLOAD_MAX_MEMORY_SIZE
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_upload_size = getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 52428800)  # default 50MB

    def __call__(self, request):
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length and int(content_length) > self.max_upload_size:
            return JsonResponse(
                {
                    "code": 400,
                    "status": "failed",
                    "message": f"The request body is too large. Maximum allowed size is {self.max_upload_size / (1024*1024)} MB",
                    "data": { "request": [f"The whole request body is too large by {int(content_length) - self.max_upload_size} bytes. Please reduce the size of 50 MB and try again."] }
                },
                status=400
            )

        response = self.get_response(request)
        return response
