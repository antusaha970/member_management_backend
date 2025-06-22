from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from . import serializers
from .models import EmailGroup, SMTPConfiguration
from rest_framework.response import Response
import logging
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
from rest_framework import status
from mails.utils.permission_classes import BulkEmailManagementPermission

from django.core.cache import cache
from django.utils.http import urlencode
from core.utils.pagination import CustomPageNumberPagination
logger = logging.getLogger("myapp")


class SetMailConfigurationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            serializer = serializers.SMTPConfigurationSerializer(
                data=request.data)
            if serializer.is_valid():
                return Response("Ok")
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Create",
                    severity_level="info",
                    description="User tried to create a mail configuration but faced an error",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=400)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Create",
                severity_level="info",
                description="User tried to create a mail configuration but faced an error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmailGroupView(APIView):
    permission_classes = [IsAuthenticated, BulkEmailManagementPermission]

    def post(self, request):
        try:
            serializer = serializers.EmailGroupSerializer(data=request.data)
            if serializer.is_valid():
                obj = serializer.save()
                name = serializer.validated_data['name']

                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Create Email Group",
                    severity_level="info",
                    description="User created an email group successfully",
                )
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Email group created successfully",
                    "data": {
                        "id": obj.id,
                        "name": name,
                    }
                    
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Create Email Group",
                    severity_level="info",
                    description="User tried to create an email group but faced an error",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Create",
                severity_level="info",
                description="User tried to create an email group but faced an error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def get(self, request):
        try:
            
            email_groups = EmailGroup.objects.all()
            serializer = serializers.EmailGroupViewSerializer(
                email_groups, many=True)
            # activity log
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve all Email Groups",
                severity_level="info",
                description="User fetched email groups successfully",
            )
            return Response({
                "code": 200,
                "status": "success",
                "message": "Email groups fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve all Email Groups",
                severity_level="errors",
                description="User tried to fetch all email groups but faced an error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, group_id):
        try:
            email_group = EmailGroup.objects.get(id=group_id)
            serializer = serializers.EmailGroupSerializer(
                email_group, data=request.data, partial=True)
            if serializer.is_valid():
                obj = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update Email Group",
                    severity_level="info",
                    description=f"User updated email group successfully",
                )
                return Response({
                    "code": 200,
                    "status": "success",
                    "message": "Email group updated successfully",
                    "data": {
                        "id": obj.id,
                        "name": obj.name,
                    }
                }, status=status.HTTP_200_OK)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update Email Group",
                    severity_level="info",
                    description=f"User tried to update email group but faced an error",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except EmailGroup.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Update Email Group",
                severity_level="errors",
                description=f"User tried to update email group but it does not exist",
            )
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Email group not found",
                "errors": {
                    "group": ["Email group not found"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Update Email Group",
                severity_level="errors",
                description=f"User tried to update email group but faced an error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, group_id):
        try:
            email_group = EmailGroup.objects.get(id=group_id)
            email_group.delete()
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Delete Email Group",
                severity_level="info",
                description=f"User deleted email group with id {group_id} successfully",
            )
            return Response({
                "code": 204,
                "status": "success",
                "message": "Email group deleted successfully"
            }, status=status.HTTP_204_NO_CONTENT)
        except EmailGroup.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Delete Email Group",
                severity_level="errors",
                description=f"User tried to delete email group but it does not exist",
            )
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Email group not found",
                "errors": {
                    "group": ["Email group not found"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Delete Email Group",
                severity_level="errors",
                description=f"User tried to delete email group but faced an error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmailGroupDetailView(APIView):
    permission_classes = [IsAuthenticated, BulkEmailManagementPermission]

    def get(self, request, group_id):
        try:
            email_group = EmailGroup.objects.get(id=group_id)
            serializer = serializers.EmailGroupViewSerializer(email_group)
            # activity log
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve specific Email Group",
                severity_level="info",
                description=f"User fetched email group with id {group_id} successfully",
            )
            return Response({
                "code": 200,
                "status": "success",
                "message": "Email group retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except EmailGroup.DoesNotExist:
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Email group not found",
                "errors": {
                    "group": ["Email group not found"]
                }
                
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve Email Group",
                severity_level="errors",
                description=f"User tried to retrieve specific email group  but faced an error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)