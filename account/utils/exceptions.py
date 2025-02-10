from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, NotAuthenticated):
        return Response(           {
            "status": 401,
            "error": "Invalid request",
            "message": "Authentication credentials were not provided."
        },status=status.HTTP_401_UNAUTHORIZED)

    
    elif isinstance(exc, PermissionDenied):
          return Response({
            "status": 403,
            "error": "Invalid request",
            "message": "You do not have permission to perform this action.",
           
        }, status=status.HTTP_403_FORBIDDEN)
    return response
