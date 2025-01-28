from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from . import serializers
from .utils.utility_functions import generate_member_id
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Member, MembersFinancialBasics


class MemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

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
                    member_ID=member.member_ID)

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

    def patch(self, request, member_id):
        member = get_object_or_404(Member, member_ID=member_id)
        member_financial_basics = get_object_or_404(
            MembersFinancialBasics, member=member)
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

    def delete(self, request, member_id):
        # find the member
        member = get_object_or_404(Member, member_ID=member_id)
        if member.status == 2:
            # if member is already deleted
            return Response({
                'detail': "member already deleted",
                'status': "failed",
            }, status=status.HTTP_400_BAD_REQUEST)
        # if not deleted then update the member status to delete
        member.status = 2
        member.save(update_fields=['status'])
        return Response({
            'detail': "member deleted",
            'status': "deleted",
        }, status=status.HTTP_204_NO_CONTENT)


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
