from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegistrationSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token


class AccountRegistrationView(APIView):
    def post(self, request):
        """
        Register a new account with valid data. 
        """
        data = request.data
        serializer = RegistrationSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "status": "success",
                "token": str(token)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {
                    'status': "failed",
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
