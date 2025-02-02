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


class MemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            member_serializer = serializers.MemberSerializer(data=data)
            member_financial_basics_serializer = serializers.MembersFinancialBasicsSerializer(
                data=data)
            is_member_serializer_valid = member_serializer.is_valid()
            is_member_financial_serializer_valid = member_financial_basics_serializer.is_valid()
            if is_member_serializer_valid and is_member_financial_serializer_valid:
                with transaction.atomic():
                    member = member_serializer.save()
                    member_financial_basics_serializer.save(
                        member_ID=member.member_ID, club=member.club.id)

                    return Response({
                        'data': {
                            'member_ID': member.member_ID,
                        },
                        'status': 'created'
                    }, status=status.HTTP_201_CREATED)
            else:
                # Merge errors from both serializers
                merged_errors = {**member_serializer.errors, **
                                 member_financial_basics_serializer.errors}
                return Response({
                    "errors": merged_errors,
                    "status": "failed"
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as server_error:
            return Response({'detail': "Internal Server Error", 'error_message': str(server_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, member_id):
        member = get_object_or_404(Member, member_ID=member_id)
        member_financial_basics = get_object_or_404(
            MembersFinancialBasics, member=member)
        try:
            data = request.data
            member_serializer = serializers.MemberSerializer(member, data=data)
            member_financial_basics_serializer = serializers.MembersFinancialBasicsSerializer(
                member_financial_basics,
                data=data)
            is_member_serializer_valid = member_serializer.is_valid()
            is_member_financial_serializer_valid = member_financial_basics_serializer.is_valid()
            if is_member_serializer_valid and is_member_financial_serializer_valid:
                with transaction.atomic():
                    member = member_serializer.save()
                    member_financial_basics_serializer.save(
                        member_ID=member.member_ID)

                    return Response({
                        'data': {
                            'member_ID': member.member_ID,
                        },
                        'status': 'updated'
                    }, status=status.HTTP_200_OK)
            else:
                # Merge errors from both serializers
                merged_errors = {**member_serializer.errors, **
                                 member_financial_basics_serializer.errors}
                return Response({
                    "errors": merged_errors,
                    "status": "failed"
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as server_error:
            return Response({'detail': "Internal Server Error", 'error_message': str(server_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, member_id):
        member = get_object_or_404(Member, member_ID=member_id)
        try:
            # find the member
            if member.status == 2:
                # if member is already deleted
                return Response({
                    'detail': "member already deleted",
                    'status': "failed",
                }, status=status.HTTP_400_BAD_REQUEST)
            # if not deleted then update the member status to delete
            with transaction.atomic():
                member.status = 2
                member.save(update_fields=['status'])
                return Response({
                    'detail': "member deleted",
                    'status': "deleted",
                }, status=status.HTTP_204_NO_CONTENT)
        except Exception as server_error:
            return Response({'detail': "Internal Server Error", 'error_message': str(server_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, member_id):
        member = get_object_or_404(Member, member_ID=member_id)  # get member
        member_financial_basics = get_object_or_404(
            MembersFinancialBasics, member=member)  # get member financial data
        try:
            # check if member status is deleted or not
            if member.status == 2:
                return Response({
                    'errors': {
                        'member_ID': [f"{member_id} member has been deleted"]
                    }
                }, status=status.HTTP_204_NO_CONTENT)
            # pass the data to the serializers
            member_serializer = serializers.MemberSerializerForViewSingleMember(
                member)
            member_financial_basics_serializer = serializers.MembersFinancialBasicsSerializerForViewSingleMember(
                member_financial_basics)
            # unwrap the data to make a single object using two serializers data
            data = {**member_serializer.data, **
                    member_financial_basics_serializer.data}
            return Response({
                'data': data
            })
        except Exception as server_error:
            return Response({'detail': "Internal Server Error", 'error_message': str(server_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberIdView(APIView):
    permission_classes = [IsAuthenticated, ViewMemberPermission]

    def post(self, request):
        try:
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
        except Exception as server_error:
            return Response({'detail': "Internal Server Error", 'error_message': str(server_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
