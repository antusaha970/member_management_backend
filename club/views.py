from rest_framework.views import APIView
from .serializers import ClubSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Club


class ClubRegisterView(APIView):
    def post(self, request):
        data = request.data
        serializer = ClubSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        clubs = Club.objects.all()
        serializer = ClubSerializer(clubs, many=True)
        return Response({
            'data': serializer.data
        }, status=status.HTTP_200_OK)
