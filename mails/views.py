from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from . import serializers
from .models import EmailGroup, SMTPConfiguration
from rest_framework.response import Response
import logging
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
from rest_framework import status
from .models import SMTPConfiguration, Email_Compose, EmailAttachment
from django.shortcuts import get_object_or_404
from django.http import Http404
from mails.utils.permission_classes import BulkEmailManagementPermission

from django.core.cache import cache
from django.utils.http import urlencode
from core.utils.pagination import CustomPageNumberPagination
from django.db import transaction
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

    def put(self, request, id):
        try:
            user = request.user
            instance = get_object_or_404(SMTPConfiguration, pk=id, user=user)
            serializer = serializers.SMTPConfigurationSerializer(
                data=request.data)
            if serializer.is_valid():
                instance = serializer.update(
                    instance, serializer.validated_data)
                return Response({
                    "code": 200,
                    "status": "success",
                    "message": "Mail configuration updated successfully",
                    "data": {
                        "id": instance.id,
                    }
                })
            else:
                return Response({
                    "code": 400,
                    "status": "Bad request",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=400)
        except Http404:
            return Response({
                "code": 404,
                "status": "Not found",
                "message": "Mail configuration not found",
            }, status=404)
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
            serializer = serializers.EmailComposeViewSerializer(
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

    def patch(self, request, id):
        try:
            user = request.user
            instance = get_object_or_404(Email_Compose, pk=id, user=user)
            serializer = serializers.EmailComposeUpdateSerializer(
                data=request.data)
            if serializer.is_valid():
                update_instance = serializer.update(
                    instance, serializer.validated_data)
                return Response({
                    "code": 200,
                    "status": "success",
                    "message": "Mail Compose updated successfully",
                    "data": {
                        "id": update_instance.id,
                    }
                }, status=200)
            else:
                return Response({
                    "code": 400,
                    "status": "Bad request",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=400)

        except Http404:
            return Response({
                "code": 404,
                "status": "Not found",
                "message": "Mail Compose not found",
            }, status=404
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Update",
                severity_level="info",
                description="User tried to update an mail Composes but faced an error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            user = request.user
            instance = get_object_or_404(Email_Compose, pk=id, user=user)
            with transaction.atomic():
                attachments = EmailAttachment.objects.filter(
                    email_compose=instance)
                attachments.delete()
                instance.delete()
            return Response({
                "code": 204,
                "status": "success",
                "message": "Mail Compose deleted successfully"
            }, status=204)
        except Http404:
            return Response({
                "code": 404,
                "status": "Not found",
                "message": "Mail Compose not found",
            }, status=404)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Update",
                severity_level="info",
                description="User tried to update an mail Composes but faced an error",
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
