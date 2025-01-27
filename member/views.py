from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from . import serializers
from .utils.utility_functions import generate_member_id
from rest_framework.response import Response
from rest_framework import status
import pdb


class MemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pass


class MemberIdView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = serializers.MemberIdSerializer(data=data)
        if serializer.is_valid():
            membership_type = serializer.validated_data['membership_type']
            id = generate_member_id(membership_type)
            return Response({
                'new_generated_id': id
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
