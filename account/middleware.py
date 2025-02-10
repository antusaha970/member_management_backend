from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings


class JWTMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
        if token:
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"
