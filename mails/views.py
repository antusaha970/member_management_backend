from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from . import serializers
from rest_framework.response import Response
import logging
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
from rest_framework import status
from .models import SMTPConfiguration, Email_Compose


logger = logging.getLogger("myapp")


class SetMailConfigurationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            serializer = serializers.SMTPConfigurationSerializer(
                data=request.data)
            if serializer.is_valid():
                user = request.user
                instance = serializer.save(user=user)
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Mail configuration created successfully",
                    "data": {
                        "id": instance.id,
                    }
                }, status=201)
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

    def get(self, request):
        try:
            user = request.user
            configs = SMTPConfiguration.objects.filter(user=user)
            serializer = serializers.SMTPConfigurationSerializer(
                configs, many=True)
            return Response({
                "code": 200,
                "status": "success",
                "message": "Mail configuration retrieved successfully",
                "data": serializer.data
            }, status=200)

        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="",
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


class EmailComposeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = serializers.EmailComposeSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user
                instance = serializer.save(user=user)
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Mail Compose created successfully",
                    "data": {
                        "id": instance.id,
                    }
                }, status=201)
            else:
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
                verb="Creation",
                severity_level="info",
                description="User tried to create a mail Compose but faced an error",
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
            user = request.user
            composes = Email_Compose.objects.filter(user=user)
            serializer = serializers.EmailComposeSerializer(
                composes, many=True)
            return Response({
                "code": 200,
                "status": "success",
                "message": "Mail Composes retrieved successfully",
                "data": serializer.data
            })

        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view all mail Composes but faced an error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
