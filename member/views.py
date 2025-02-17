from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from . import serializers
from .utils.utility_functions import generate_member_id
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Member, MembersFinancialBasics
from .utils.permission_classes import ViewMemberPermission
import pdb


class MemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            member_serializer = serializers.MemberSerializer(data=data)
            is_member_serializer_valid = member_serializer.is_valid()
            if is_member_serializer_valid:
                with transaction.atomic():
                    member = member_serializer.save()
                    return Response({
                        'code': 201,
                        'status': 'success',
                        'message': "Member created successfully",
                        'data': {
                            'member_ID': member.member_ID,
                        },
                    }, status=status.HTTP_201_CREATED)
            else:
                # Merge errors from both serializers
                merged_errors = {**member_serializer.errors}
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Member creation failed",
                    "errors": merged_errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as server_error:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(server_error)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, member_id):
        try:
            member = get_object_or_404(Member, member_ID=member_id)
            data = request.data
            member_serializer = serializers.MemberSerializer(member, data=data)
            is_member_serializer_valid = member_serializer.is_valid()
            if is_member_serializer_valid:
                with transaction.atomic():
                    member = member_serializer.save()
                    return Response({
                        'code': 200,
                        'status': 'success',
                        'message': "Member updated successfully",
                        'data': {
                            'member_ID': member.member_ID,
                        }
                    }, status=status.HTTP_200_OK)
            else:
                # Merge errors from both serializers
                merged_errors = {**member_serializer.errors}
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Member update failed",
                    "errors": merged_errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as server_error:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(server_error)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, member_id):
        try:
            member = get_object_or_404(Member, member_ID=member_id)
            # find the member
            if member.status == 2:
                # if member is already deleted
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Member is already deleted",
                }, status=status.HTTP_400_BAD_REQUEST)
            # if not deleted then update the member status to delete
            with transaction.atomic():
                member.status = 2
                member.save(update_fields=['status'])
                return Response({
                    "code": 204,
                    'message': "member deleted",
                    'status': "success",
                }, status=status.HTTP_204_NO_CONTENT)
        except Exception as server_error:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(server_error)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, member_id):
        try:
            member = get_object_or_404(
                Member, member_ID=member_id)  # get member
            # check if member status is deleted or not
            if member.status == 2:
                return Response({
                    "code": 204,
                    "status": "failed",
                    "message": "Member is already deleted",
                    'errors': {
                        'member_ID': [f"{member_id} member has been deleted"]
                    }
                }, status=status.HTTP_204_NO_CONTENT)
            # pass the data to the serializers
            member_serializer = serializers.MemberSerializerForViewSingleMember(
                member)
            # unwrap the data to make a single object using two serializers data
            data = {**member_serializer.data}
            return Response({
                "code": 200,
                "status": "success",
                "message": f"View member information for member {member_id}",
                'data': data
            }, status=status.HTTP_200_OK)
        except Exception as server_error:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(server_error)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberIdView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberIdSerializer(data=data)
            if serializer.is_valid():
                membership_type = serializer.validated_data['membership_type']
                id = generate_member_id(membership_type)
                return Response({
                    "code": 200,
                    "status": "success",
                    "message": "Generated Member Id successfully",
                    "data": {
                        'new_generated_id': id
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Failed to generate member Id",
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as server_error:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(server_error)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberContactNumberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberContactNumberSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                return Response({
                    "code": 201,
                    "message": "Member contact number has been created successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberEmailAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberEmailAddressSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                return Response({
                    "code": 201,
                    "message": "Member Email address has been created successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberAddressSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                return Response({
                    "code": 201,
                    "message": "Member address has been created successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
