
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from . import serializers
from .utils.utility_functions import generate_member_id
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Member, MembersFinancialBasics, MemberHistory, CompanionInformation, Documents
from .utils.permission_classes import ViewMemberPermission, AddMemberPermission, UpdateMemberPermission, DeleteMemberPermission
import logging
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
from core.models import MembershipType
from datetime import datetime
from django.utils import timezone
from core.utils.pagination import CustomPageNumberPagination
from .import models
import pdb
from .models import Spouse, Profession
from .tasks import delete_member_model_dependencies
logger = logging.getLogger("myapp")


class MemberView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [UpdateMemberPermission()]
        elif self.request.method == "DELETE":
            return [DeleteMemberPermission()]
        elif self.request.method == "GET":
            return [ViewMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            member_serializer = serializers.MemberSerializer(data=data)
            is_member_serializer_valid = member_serializer.is_valid()
            if is_member_serializer_valid:
                with transaction.atomic():
                    member = member_serializer.save()
                    log_activity_task.delay_on_commit(
                        request_data_activity_log(request),
                        verb="Member create",
                        severity_level="info",
                        description="A new member has been created by the user",
                    )
                    MemberHistory.objects.create(start_date=timezone.now(
                    ), stored_member_id=member.member_ID, member=member)
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
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Member creation failed",
                    severity_level="info",
                    description="user tried to create a member but made an invalid request",
                )
                merged_errors = {**member_serializer.errors}
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Member creation failed",
                    "errors": merged_errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as server_error:
            logger.exception(str(server_error))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Member creation failed",
                severity_level="info",
                description="user tried to create a member but made an invalid request",
            )
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
            member = Member.objects.get(member_ID=member_id)
            data = request.data
            member_serializer = serializers.MemberSerializer(member, data=data)
            is_member_serializer_valid = member_serializer.is_valid()
            if is_member_serializer_valid:
                with transaction.atomic():
                    member = member_serializer.save()
                    # member_ID=member.member_ID
                    log_activity_task.delay_on_commit(
                        request_data_activity_log(request),
                        verb="Member update success",
                        severity_level="info",
                        description="user updated a member successfully",
                    )
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
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Member update failed",
                    severity_level="info",
                    description="user tried to update member but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Member update failed",
                    "errors": merged_errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Member.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Member update failed",
                severity_level="info",
                description="user tried to update member but made an invalid request",
            )
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Member not found",
                "errors": {
                    "member": ["Member not found by this member_ID"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as server_error:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Member update failed",
                severity_level="info",
                description="user tried to update member but made an invalid request",
            )
            logger.exception(str(server_error))
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
            member = Member.objects.get(member_ID=member_id)
            # find the member
            if member.status == 2:
                # if member is already deleted
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Member delete failed",
                    severity_level="info",
                    description="user tried to delete member but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Member is already deleted",
                }, status=status.HTTP_400_BAD_REQUEST)
            # if not deleted then update the member status to delete
            with transaction.atomic():
                all_instance = MemberHistory.objects.filter(member=member)
                update_lst = []
                for instance in all_instance:
                    instance.end_date = timezone.now()
                    instance.transferred_reason = "deleted"
                    instance.transferred = True
                    update_lst.append(instance)
                MemberHistory.objects.bulk_update(
                    update_lst, ["end_date", "transferred_reason", "transferred"])
                member.member_ID = None
                member.status = 2
                member.is_active = False
                member.save(update_fields=['status', 'member_ID', 'is_active'])
                delete_member_model_dependencies.delay_on_commit(member.id)
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Member delete success",
                    severity_level="info",
                    description="user tried to delete a member and succeeded",
                )
                return Response({
                    "code": 204,
                    'message': "member deleted",
                    'status': "success",
                }, status=status.HTTP_204_NO_CONTENT)

        except Member.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Member delete failed",
                severity_level="error",
                description="user tried to delete member but made an invalid request",
            )
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Member not found",
                "errors": {
                    "member": ["Member not found by this member_ID"]
                }
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as server_error:
            logger.exception(str(server_error))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Member delete failed",
                severity_level="error",
                description="user tried to delete member but made an invalid request",
            )
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
            member = Member.objects.get(member_ID=member_id)
            # check if member status is deleted or not
            if member.status == 2:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Member view failed",
                    severity_level="warning",
                    description="user tried to view a member but made an invalid request",
                )
                return Response({
                    "code": 204,
                    "status": "failed",
                    "message": "Member is already deleted",
                    'errors': {
                        'member_ID': [f"{member_id} member has been deleted"]
                    }
                }, status=status.HTTP_204_NO_CONTENT)
            contact_numbers = models.ContactNumber.objects.filter(
                member=member)
            emails = models.Email.objects.filter(
                member=member)
            addresses = models.Address.objects.filter(
                member=member)
            spouse = models.Spouse.objects.filter(
                member=member)
            descendant = models.Descendant.objects.filter(
                member=member)
            emergency = models.EmergencyContact.objects.filter(
                member=member)
            companion = models.CompanionInformation.objects.filter(
                member=member)
            certificate = models.Certificate.objects.filter(member=member)
            documents = models.Documents.objects.filter(
                member=member)
            jobs = models.Profession.objects.filter(member=member)
            special_days = models.SpecialDay.objects.filter(member=member)
            # pass the data to the serializers
            member_serializer = serializers.MemberSerializerForViewSingleMember(
                member)
            contact_serializer = serializers.MemberContactNumberViewSerializer(
                contact_numbers, many=True)
            email_serializer = serializers.MemberEmailAddressViewSerializer(
                emails, many=True)
            address_serializer = serializers.MemberAddressViewSerializer(
                addresses, many=True)
            spouse_serializer = serializers.MemberSpouseViewSerializer(
                spouse, many=True)
            descendant_serializer = serializers.MemberDescendantsViewSerializer(
                descendant, many=True)
            emergency_serializer = serializers.MemberEmergencyContactViewSerializer(
                emergency, many=True)
            companion_serializer = serializers.MemberCompanionViewSerializer(
                companion, many=True)
            documents_serializer = serializers.MemberDocumentsViewSerializer(
                documents, many=True)
            jon_serializer = serializers.MemberJobViewSerializer(
                jobs, many=True)
            certificate_serialzier = serializers.MemberCertificateViewSerializer(
                certificate, many=True)
            special_days_serializer = serializers.MemberSpecialDaysViewSerializer(
                special_days, many=True)
            # unwrap the data to make a single object using two serializers data
            data = {
                'member_info': member_serializer.data,
                'contact_info': contact_serializer.data,
                'email_address': email_serializer.data,
                'address': address_serializer.data,
                'job': jon_serializer.data,
                'spouse': spouse_serializer.data,
                'descendant': descendant_serializer.data,
                'emergency_contact': emergency_serializer.data,
                'certificate': certificate_serialzier.data,
                'companion': companion_serializer.data,
                'document': documents_serializer.data,
                'special_days': special_days_serializer.data,
            }
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Member view successfully",
                severity_level="info",
                description="user tried to view a member and succeeded",
            )
            return Response({
                "code": 200,
                "status": "success",
                "message": f"View member information for member {member_id}",
                'data': data
            }, status=status.HTTP_200_OK)
        except Member.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Member view failed",
                severity_level="error",
                description="user tried to view a member but made an invalid request",
            )
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Member not found",
                "errors": {
                    "member": ["Member not found by this member_ID"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as server_error:
            logger.exception(str(server_error))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Member view failed",
                severity_level="error",
                description="user tried to view a member but made an invalid request",
            )
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
                all_id = generate_member_id(membership_type)
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Member id view succeeded",
                    severity_level="info",
                    description="user tried to view member id and succeeded",
                )
                return Response({
                    "code": 200,
                    "status": "success",
                    "message": "Generated Member Id successfully",
                    "data": all_id
                }, status=status.HTTP_200_OK)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Member id view failed",
                    severity_level="error",
                    description="user tried to view member id but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Failed to generate member Id",
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as server_error:
            logger.exception(str(server_error))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Member id view failed",
                severity_level="error",
                description="user tried to view member id but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(server_error)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberContactNumberView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [IsAuthenticated(), UpdateMemberPermission()]
        else:
            return [AllowAny()]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberContactNumberSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Added member contact number",
                    severity_level="info",
                    description="user tried to add member contact number and succeeded",
                )
                return Response({
                    "code": 201,
                    "message": "Member contact number has been created successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Failed to add member contact number",
                    severity_level="error",
                    description="user tried to add member contact number but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Failed to add member contact number",
                severity_level="error",
                description="user tried to add member contact number but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, member_ID):
        try:
            member = get_object_or_404(Member, member_ID=member_ID)
            data = request.data
            serializer = serializers.MemberContactNumberSerializer(
                member, data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save(instance=member)
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update member contact number",
                    severity_level="info",
                    description="user tried to update member contact number and succeeded",
                )
                return Response({
                    "code": 200,
                    "message": "Member contact number has been created successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_200_OK)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update member contact number failed",
                    severity_level="error",
                    description="user tried to update member contact number but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Update member contact number failed",
                severity_level="error",
                description="user tried to update member contact number but made an invalid request",
            )
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

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [UpdateMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberEmailAddressSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Added member Email addresses",
                    severity_level="info",
                    description="user tried to add member email addresses and succeeded",
                )
                return Response({
                    "code": 201,
                    "message": "Member Email address has been created successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Added member email addresses failed",
                    severity_level="error",
                    description="user tried to add member email addresses and failed",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Added member email address failed",
                severity_level="error",
                description="user tried to add member email address and failed",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, member_ID):
        try:
            member = get_object_or_404(Member, member_ID=member_ID)
            data = request.data
            serializer = serializers.MemberEmailAddressSerializer(
                member, data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save(instance=member)
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update member email address",
                    severity_level="info",
                    description="user tried to update member email address and succeeded"
                )
                return Response({
                    "code": 200,
                    "message": "Member Email address has been updated successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_200_OK)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update member email address failed",
                    severity_level="error",
                    description="user tried to update member email address but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Update member email address failed",
                severity_level="error",
                description="user tried to update member email address but made an invalid request",
            )
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

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [UpdateMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberAddressSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Added member address successful",
                    severity_level="info",
                    description="user tried to add member address and succeeded",
                )
                return Response({
                    "code": 201,
                    "message": "Member address has been created successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Added member address failed",
                    severity_level="error",
                    description="user tried to add member address but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Added member address failed",
                severity_level="error",
                description="user tried to add member address but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, member_ID):
        try:
            member = get_object_or_404(Member, member_ID=member_ID)
            data = request.data
            serializer = serializers.MemberAddressSerializer(member, data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save(instance=member)
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update member address successful",
                    severity_level="info",
                    description="user tried to update member address and successful",
                )
                return Response({
                    "code": 200,
                    "message": "Member address has been updated successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_200_OK)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update member address failed",
                    severity_level="error",
                    description="user tried to update member address but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Update member address failed",
                severity_level="error",
                description="user tried to update member address but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberSpouseView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [UpdateMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberSpouseSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Added member spouse successful",
                    severity_level="info",
                    description="user tried to add member spouse and succeeded",
                )
                return Response({
                    "code": 201,
                    "message": "Member address has been created successfully",
                    "status": "success",
                    "data": {
                        "spouse_id": instance.id
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Added member spouse failed",
                    severity_level="error",
                    description="user tried to add member spouse but made an invalid",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Added member spouse failed",
                severity_level="error",
                description="user tried to add member spouse but made an invalid",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        try:
            data = request.data
            id = data.get('id')
            if id:
                instance = models.Spouse.objects.get(pk=id)
                serializer = serializers.MemberSpouseSerializer(
                    instance, data=data)
            else:
                instance = None
                serializer = serializers.MemberSpouseSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    if instance is not None:
                        instance = serializer.save(instance=instance)
                        log_activity_task.delay_on_commit(
                            request_data_activity_log(request),
                            verb="Update member spouse succeeded",
                            severity_level="info",
                            description="user tried to update member spouse and succeeded",
                        )
                        return Response({
                            "code": 200,
                            "message": "Member Spouse has been updated successfully",
                            "status": "success",
                            "data": {
                                "spouse_id": instance.id
                            }
                        }, status=status.HTTP_200_OK)
                    else:
                        instance = serializer.save()
                        log_activity_task.delay_on_commit(
                            request_data_activity_log(request),
                            verb="Update member spouse succeeded",
                            severity_level="info",
                            description="user tried to update member spouse and succeeded",
                        )
                        return Response({
                            "code": 201,
                            "message": "Member spouse has been created successfully",
                            "status": "success",
                            "data": {
                                "spouse_id": instance.id
                            }
                        }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update member spouse failed",
                    severity_level="error",
                    description="user tried to update member spouse but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Update member spouse failed",
                severity_level="error",
                description="user tried to update member spouse but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberDescendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [UpdateMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberDescendantsSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Add member descendants successful",
                    severity_level="info",
                    description="user tried to add member descendants and succeeded",
                )
                return Response({
                    "code": 201,
                    "message": "Member Descendant has been created successfully",
                    "status": "success",
                    "data": {
                        "descendant_id": instance.id
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Add member descendants failed",
                    severity_level="error",
                    description="user tried to add member descendants but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Add member descendants failed",
                severity_level="error",
                description="user tried to add member descendants but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        try:
            data = request.data
            id = data.get('id')
            if id:
                instance = models.Descendant.objects.get(pk=id)
                serializer = serializers.MemberDescendantsSerializer(
                    instance, data=data)
            else:
                instance = None
                serializer = serializers.MemberDescendantsSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    if instance is not None:
                        instance = serializer.save(instance=instance)
                        log_activity_task.delay_on_commit(
                            request_data_activity_log(request),
                            verb="Update member descendants succeeded",
                            severity_level="info",
                            description="user tried to update member descendants and succeeded",
                        )
                        return Response({
                            "code": 200,
                            "message": "Member Descendant has been updated successfully",
                            "status": "success",
                            "data": {
                                "descendant_id": instance.id
                            }
                        }, status=status.HTTP_200_OK)
                    else:
                        instance = serializer.save()
                        log_activity_task.delay_on_commit(
                            request_data_activity_log(request),
                            verb="Update member descendants succeeded",
                            severity_level="info",
                            description="user tried to update member descendants and succeeded",
                        )
                        return Response({
                            "code": 201,
                            "message": "Member Descendant has been created successfully",
                            "status": "success",
                            "data": {
                                "descendant_id": instance.id
                            }
                        }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update member descendants failed",
                    severity_level="error",
                    description="user tried to update member descendants but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Update member descendants failed",
                severity_level="error",
                description="user tried to update member descendants but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberJobView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [UpdateMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberJobSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Add member job information",
                    severity_level="info",
                    description="user tried to add member job information and succeeded",
                )
                return Response({
                    "code": 201,
                    "message": "Member job has been created successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Add member job information failed",
                    severity_level="error",
                    description="user tried to add member job information but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Add member job information failed",
                severity_level="error",
                description="user tried to add member job information but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, member_ID):
        try:
            member = get_object_or_404(Member, member_ID=member_ID)
            data = request.data
            serializer = serializers.MemberJobSerializer(member, data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save(instance=member)
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update member job information succeeded",
                    severity_level="info",
                    description="user tried to update member job information  and succeeded",
                )
                return Response({
                    "code": 200,
                    "message": "Member job has been updated successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_200_OK)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update member job information failed",
                    severity_level="error",
                    description="user tried to update member job information but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Update member job information failed",
                severity_level="error",
                description="user tried to update member job information but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberEmergencyContactView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [UpdateMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberEmergencyContactSerializer(
                data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()

                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Emergency contact created",
                    severity_level="info",
                    description="A user has successfully added a new emergency contact.",
                )
                return Response({
                    "code": 201,
                    "message": "Member Emergency contact has been created successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Emergency contact creation failed",
                    severity_level="error",
                    description="A user tried to create a emergency contact but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Emergency contact creation failed",
                severity_level="error",
                description="A user tried to create a emergency contact but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, member_ID):
        try:
            member = get_object_or_404(Member, member_ID=member_ID)
            data = request.data
            serializer = serializers.MemberEmergencyContactSerializer(member,
                                                                      data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save(instance=member)
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Emergency contact updated",
                    severity_level="info",
                    description="A user has successfully updated an emergency contact.",
                )
                return Response({
                    "code": 200,
                    "message": "Member Emergency contact has been updated successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_200_OK)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Emergency contact update failed",
                    severity_level="error",
                    description="A user tried to update an emergency contact but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Emergency contact update failed",
                severity_level="error",
                description="A user tried to update an emergency contact but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberCompanionView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [UpdateMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberCompanionInformationSerializer(
                data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Companion information created",
                    severity_level="info",
                    description="A user has successfully added a new companion information.",
                )
                return Response({
                    "code": 201,
                    "message": "Member Companion has been created successfully",
                    "status": "success",
                    "data": {
                        "companion_id": instance.id
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Companion information creation failed",
                    severity_level="error",
                    description="A user tried to create a companion information but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Companion information creation failed",
                severity_level="error",
                description="A user tried to create a companion information but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        try:
            data = request.data
            id = data.get('id')
            if id:
                instance = models.CompanionInformation.objects.get(pk=id)
                serializer = serializers.MemberCompanionInformationSerializer(
                    instance, data=data)
            else:
                instance = None
                serializer = serializers.MemberCompanionInformationSerializer(
                    data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    if instance is not None:
                        instance = serializer.save(instance=instance)
                        log_activity_task.delay_on_commit(
                            request_data_activity_log(request),
                            verb="Companion information updated",
                            severity_level="info",
                            description="A user has successfully updated a new companion.",
                        )
                        return Response({
                            "code": 200,
                            "message": "Member companion has been updated successfully",
                            "status": "success",
                            "data": {
                                "companion_id": instance.id
                            }
                        }, status=status.HTTP_200_OK)
                    else:
                        instance = serializer.save()
                        log_activity_task.delay_on_commit(
                            request_data_activity_log(request),
                            verb="Companion information created",
                            severity_level="info",
                            description="A user has successfully added a new companion information.",
                        )
                        return Response({
                            "code": 201,
                            "message": "Member companion has been created successfully",
                            "status": "success",
                            "data": {
                                "companion_id": instance.id
                            }
                        }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Companion information update failed",
                    severity_level="error",
                    description="A user tried to update a companion information but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Companion information update failed",
                severity_level="error",
                description="A user tried to update a companion information but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [UpdateMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.MemberDocumentSerializer(
                data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Member documents created",
                    severity_level="info",
                    description="A user has successfully added new member documents.",
                )
                return Response({
                    "code": 201,
                    "message": "Member documents has been added successfully",
                    "status": "success",
                    "data": {
                        "document_id": instance.id
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Member documents creation failed",
                    severity_level="error",
                    description="A user tried to create member documents but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Member documents creation failed",
                severity_level="error",
                description="A user tried to create member documents but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        try:
            data = request.data
            id = data.get('id')
            if id:
                instance = models.Documents.objects.get(pk=id)
                serializer = serializers.MemberDocumentSerializer(
                    instance, data=data)

            else:
                instance = None
                serializer = serializers.MemberDocumentSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    if instance is not None:
                        instance = serializer.save(instance=instance)
                        log_activity_task.delay_on_commit(
                            request_data_activity_log(request),
                            verb="Member documents updated",
                            severity_level="info",
                            description="A user has successfully updated a new member document.",
                        )
                        return Response({
                            "code": 200,
                            "message": "Member Documents has been updated successfully",
                            "status": "success",
                            "data": {
                                "document_id": instance.id
                            }
                        }, status=status.HTTP_200_OK)
                    else:
                        instance = serializer.save()
                        log_activity_task.delay_on_commit(
                            request_data_activity_log(request),
                            verb="Member documents created",
                            severity_level="info",
                            description="A user has successfully added a new member document.",
                        )
                        return Response({
                            "code": 201,
                            "message": "Member Document has been created successfully",
                            "status": "success",
                            "data": {
                                "document_id": instance.id
                            }
                        }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Member documents update failed",
                    severity_level="error",
                    description="A user tried to update a member document but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Member documents update failed",
                severity_level="error",
                description="A user tried to update a member document but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddMemberIDview(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [UpdateMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.AddFlexibleMemberIdSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="New member id created",
                    severity_level="info",
                    description="A user has successfully created a new Member ID.",
                )
                return Response({"code": 201, "status": "success", "message": "New Id has been created"}, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="New member id creation failed",
                    severity_level="error",
                    description="A user tried to create a new Member ID but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="New member id creation failed",
                severity_level="error",
                description="A user tried to create a new Member ID but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            history = MemberHistory.objects.all()

            # Get query parameters
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")
            transferred = request.query_params.get("transferred")

            # Apply filters if query parameters exist
            if start_date and end_date:
                history = history.filter(
                    start_date__date__gte=start_date, end_date__date__lte=end_date)
            elif start_date:
                history = history.filter(start_date__date__gte=start_date)
            elif end_date:
                history = history.filter(end_date__date__lte=end_date)
            if transferred:
                if transferred == "true":
                    transferred = True
                elif transferred == "false":
                    transferred = False
                if isinstance(transferred, bool):
                    history = history.filter(transferred=transferred)

            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                history, request, view=self)
            serializer = serializers.MemberHistorySerializer(
                paginated_queryset, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Viewing all member history",
                severity_level="info",
                description="A user has successfully viewing all members history.",
            )
            return paginator.get_paginated_response({
                "code": 200,
                "status": "success",
                "message": "Viewing all members history",
                "data": serializer.data
            }, 200)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Viewing all member history failed",
                severity_level="error",
                description="A user tried to view all members history but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberSingleHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, member_ID):
        try:
            member_history = MemberHistory.objects.get(
                member__member_ID=member_ID)
            serializer = serializers.MemberHistorySerializer(
                member_history, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Viewing single member history",
                severity_level="info",
                description="A user has successfully viewing single member history.",
            )
            return Response({
                'code': 200,
                'status': 'success',
                "message": "viewing member history",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except MemberHistory.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Viewing single member history failed",
                severity_level="info",
                description="A user has viewing single member history but made an invalid request.",
            )
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Member not found",
                "errors": {
                    "member": ["Member not found by this member_ID"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Viewing single member history failed",
                severity_level="error",
                description="A user tried to view single member history but made an invalid request.",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberSpecialDayView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [UpdateMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            # pdb.set_trace()
            serializer = serializers.MemberSpecialDaySerializer(data=data)

            if serializer.is_valid():
                instances = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="member special days created",
                    severity_level="info",
                    description="A user has successfully created new member special days.",
                )

                return Response({
                    "code": 201,
                    "status": "success",
                    "message": " Member Special Days has been created successfully",
                    "data": instances
                }, status=status.HTTP_201_CREATED)

            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="member special days creation failed",
                    severity_level="error",
                    description="A user tried to create new member special days but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="member special days creation failed",
                severity_level="error",
                description="A user tried to create new member special days but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, member_ID):
        try:
            member = get_object_or_404(Member, member_ID=member_ID)
            data = request.data
            serializer = serializers.MemberSpecialDaySerializer(
                member, data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save(instance=member)
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="member special days updated",
                    severity_level="info",
                    description="A user has successfully updated member special days.",
                )
                return Response({
                    "code": 200,
                    "message": "Member special day has been updated successfully",
                    "status": "success",
                    "data": instance
                }, status=status.HTTP_200_OK)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="member special days update failed",
                    severity_level="error",
                    description="A user tried to update member special days but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="member special days update failed",
                severity_level="error",
                description="A user tried to update member special days but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberCertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AddMemberPermission()]
        elif self.request.method == "PATCH":
            return [UpdateMemberPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        try:
            data = request.data
            # pdb.set_trace()
            serializer = serializers.MemberCertificateSerializer(data=data)

            if serializer.is_valid():
                instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="member certificates created",
                    severity_level="info",
                    description="A user has successfully created new member certificates.",
                )

                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Member Certificate has been created successfully",
                    "data": {"id": instance.id, "title": instance.title}
                }, status=status.HTTP_201_CREATED)

            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="member certificates creation failed",
                    severity_level="error",
                    description="A user tried to create new member certificates but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="member certificates creation failed",
                severity_level="error",
                description="A user tried to create new member certificates but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        try:
            data = request.data
            id = data.get('id')
            if id:
                instance = models.Certificate.objects.get(pk=id)
                serializer = serializers.MemberCertificateSerializer(
                    instance, data=data)
            else:
                instance = None
                serializer = serializers.MemberCertificateSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    if instance is not None:
                        instance = serializer.save(instance=instance)
                        log_activity_task.delay_on_commit(
                            request_data_activity_log(request),
                            verb="member certificates updated",
                            severity_level="info",
                            description="A user has successfully updated member certificates.",
                        )
                        return Response({
                            "code": 200,
                            "message": "Member Certificate has been updated successfully",
                            "status": "success",
                            "data": {
                                "certificate_id": instance.id
                            }
                        }, status=status.HTTP_200_OK)
                    else:
                        instance = serializer.save()
                        log_activity_task.delay_on_commit(
                            request_data_activity_log(request),
                            verb="member certificates created",
                            severity_level="info",
                            description="A user has successfully created new member certificates.",
                        )
                        return Response({
                            "code": 201,
                            "message": "Member Certificate has been created successfully",
                            "status": "success",
                            "data": {
                                "certificate_id": instance.id
                            }
                        }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="member certificates update failed",
                    severity_level="error",
                    description="A user tried to update member certificates but made an invalid request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="member certificates update failed",
                severity_level="error",
                description="A user tried to update member certificates but made an invalid request",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
