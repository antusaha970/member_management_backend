from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, NotAuthenticated):
        return Response({
            "code": 401,
            "status": "failed",
            "message": "Authentication credentials were not provided.",
            "errors": {
                "request": ["Invalid request"]
            },
        }, status=status.HTTP_401_UNAUTHORIZED)

    elif isinstance(exc, PermissionDenied):
        return Response({
            "code": 403,
            "status": "failed",
            "message": "You do not have permission to perform this action.",
            "errors": {
                "request": ["Invalid request"]
            },

        }, status=status.HTTP_403_FORBIDDEN)
    return response
