from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework.response import Response
from rest_framework import status

class MemberView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        
        data = request.data
        serializer= MemberSerializer(data=data)
        if serializer.is_valid():
            return Response("OK")
        else:
            return Response({
                "errors":serializer.errors,
                "status":"failed"
            },status=status.HTTP_400_BAD_REQUEST)