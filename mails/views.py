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