import pdb
from .tasks import delete_email_list_cache, bulk_email_send_task
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from member.models import Email
from . import serializers
from .models import EmailGroup, SMTPConfiguration, EmailList, SingleEmail, EmailCompose, EmailAttachment, Outbox
from rest_framework.response import Response
import logging
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import Http404
from mails.utils.permission_classes import BulkEmailManagementPermission
from activity_log.utils.functions import log_request
from .filters import EmailListFilter
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
            serializer = serializers.SMTPConfigurationSerializerForView(
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
            instance = SMTPConfiguration.objects.get(pk=id, user=user)
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
        except SMTPConfiguration.DoesNotExist:
            return Response({
                "code": 404,
                "status": "Not found",
                "message": "Mail configuration not found",
                "errors": {
                    "id": ["Mail configuration not found for the given id"]
                }
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

    def delete(self, request, id):
        try:
            user = request.user
            instance = SMTPConfiguration.objects.get(pk=id, user=user)
            with transaction.atomic():
                instance.delete()
            return Response({
                "code": 204,
                "status": "success",
                "message": "Mail configuration deleted successfully",
            }, status=204)

        except SMTPConfiguration.DoesNotExist:
            return Response({
                "code": 404,
                "status": "Not found",
                "message": "Mail configuration not found",
                "errors": {
                    "id": ["Mail configuration not found for the given id"]
                }
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
            paginator = CustomPageNumberPagination()
            composes = EmailCompose.objects.filter(user=user).order_by('id')
            paginated_qs = paginator.paginate_queryset(
                composes, request, view=self)
            serializer = serializers.EmailComposeViewSerializer(
                paginated_qs, many=True)
            return paginator.get_paginated_response({
                "code": 200,
                "status": "success",
                "message": "Mail Composes retrieved successfully",
                "data": serializer.data
            }, status=200)

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


class EmailComposeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            user = request.user
            instance = EmailCompose.objects.get(pk=id, user=user)
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
        except EmailCompose.DoesNotExist:
            return Response({
                "code": 404,
                "status": "Not found",
                "message": "Mail Compose not found",
                "errors": {
                    "id": ["Mail Compose not found for the given id"]
                }
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

    def delete(self, request, id):
        try:
            user = request.user
            instance = EmailCompose.objects.get(pk=id, user=user)
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

        except EmailCompose.DoesNotExist:
            return Response({
                "code": 404,
                "status": "Not found",
                "message": "Mail Compose not found",
                "errors": {
                    "id": ["Mail Compose not found for the given id"]
                }
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

    def get(self, request, id):
        try:
            user = request.user
            composes = get_object_or_404(EmailCompose, pk=id, user=user)
            serializer = serializers.EmailComposeViewSerializer(
                composes)
            return Response({
                "code": 200,
                "status": "success",
                "message": "Mail Compose retrieved successfully",
                "data": serializer.data
            }, status=200)
        except Http404:
            return Response({
                "code": 404,
                "status": "Not found",
                "message": "Mail Compose not found"
            }, status=404)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view a mail Compose but faced an error",
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
                # Clear cache for email lists
                delete_email_list_cache.delay()
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

    def patch(self, request, group_id):
        try:
            email_group = EmailGroup.objects.get(id=group_id)
            serializer = serializers.EmailGroupSerializer(
                email_group, data=request.data, partial=True)
            if serializer.is_valid():
                obj = serializer.update(email_group, serializer.validated_data)
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Update Email Group",
                    severity_level="info",
                    description=f"User updated email group successfully",
                )
                # Clear cache for email lists
                delete_email_list_cache.delay()
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
            # remove cache for email lists
            delete_email_list_cache.delay()
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


class EmailListView(APIView):
    permission_classes = [IsAuthenticated, BulkEmailManagementPermission]

    def post(self, request):
        try:
            serializer = serializers.EmailListSerializer(data=request.data)
            if serializer.is_valid():
                objs = serializer.save()
                print(objs)
                group = serializer.validated_data['group']
                # activity log
                log_request(request, "Create Email List", "info",
                            "User created email list successfully")
                # Clear cache for email lists
                delete_email_list_cache.delay()
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Email list created successfully",
                    "data": {
                        # "id": obj.count(),
                        "group": group.id,
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                # activity log
                log_request(request, "Create Email List", "info",
                            "User tried to create email list but faced an error")
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            # activity log
            log_request(request, "Create Email List", "errors",
                        "User tried to create email list but faced an error")

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
            query_params = request.query_params
            query_items = sorted(query_params.items())
            query_string = urlencode(query_items) if query_items else "default"
            cache_key = f"email_lists::{query_string}"

            cached_response = cache.get(cache_key)
            if cached_response:
                print(f"Cache hit for key: {cache_key}")
                return Response(cached_response, status=200)

            email_lists = EmailList.objects.all().order_by('id')
            paginator = CustomPageNumberPagination()
            filtered_qs = EmailListFilter(
                query_params, queryset=email_lists).qs
            paginated_qs = paginator.paginate_queryset(
                filtered_qs, request, view=self)
            serializer = serializers.EmailListViewSerializer(
                paginated_qs, many=True)

            response_data = {
                "code": 200,
                "status": "success",
                "message": "Email lists retrieved successfully",
                "data": serializer.data
            }

            # Cache for 2 minutes
            cache.set(cache_key, response_data, 60 * 30)
            log_request(request, "Retrieve Email Lists", "info",
                        "User fetched email lists successfully")

            return paginator.get_paginated_response(response_data, status=200)

        except Exception as e:
            logger.exception(str(e))
            log_request(request, "Retrieve Email Lists", "errors",
                        "User tried to fetch email lists but faced an error")
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailListDetailView(APIView):
    permission_classes = [IsAuthenticated, BulkEmailManagementPermission]

    def get(self, request, id):
        try:
            email_list = EmailList.objects.get(id=id)
            serializer = serializers.EmailListViewSerializer(email_list)
            log_request(request, "Retrieve Email List", "info",
                        "User retrieved email list successfully")
            return Response({
                "code": 200,
                "status": "success",
                "message": "Email list retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except EmailList.DoesNotExist:
            log_request(request, "Retrieve Email List", "errors",
                        "User tried to fetch email list but it does not exist")
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Email list not found",
                "errors": {
                    "id": ["Email list not found for the given id"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_request(request, "Retrieve Email List", "errors",
                        "User tried to fetch email list but faced an error")
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
            email_list = EmailList.objects.get(id=id)
            serializer = serializers.EmailListSingleSerializer(
                email_list, data=request.data, partial=True)
            if serializer.is_valid():
                obj = serializer.update(email_list, serializer.validated_data)
                log_request(request, "Update Email List", "info",
                            "User updated email list successfully")
                # Clear cache for email lists
                delete_email_list_cache.delay()
                return Response({
                    "code": 200,
                    "status": "success",
                    "message": "Email list updated successfully",
                    "data": {
                        "id": obj.id,
                        "email": obj.email
                    }
                }, status=status.HTTP_200_OK)
            else:
                log_request(request, "Update Email List", "errors",
                            f"User tried to update email list but faced an error: {serializer.errors}")
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except EmailList.DoesNotExist:
            log_request(request, "Update Email List", "errors",
                        f"User tried to update email list but it does not exist")
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Email list not found",
                "errors": {
                    "id": ["Email list not found for the given id"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_request(request, "Update Email List", "errors",
                        "User tried to update email list but faced an error")
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
            email_list = EmailList.objects.get(id=id)
            email_list.delete()
            log_request(request, "Delete Email List", "info",
                        "User deleted email list successfully")
            # Clear cache for email lists
            delete_email_list_cache.delay()
            return Response({
                "code": 204,
                "status": "success",
                "message": "Email list deleted successfully"
            }, status=status.HTTP_204_NO_CONTENT)
        except EmailList.DoesNotExist:
            log_request(request, "Delete Email List", "errors",
                        "User tried to delete email list but it does not exist")
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Email list not found",
                "errors": {
                    "id": ["Email list not found for the given id"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_request(request, "Delete Email List", "errors",
                        "User tried to delete email list but faced an error")
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SingleEmailView(APIView):
    permission_classes = [IsAuthenticated, BulkEmailManagementPermission]

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.SingleEmailSerializer(data=data)
            if serializer.is_valid():
                obj = serializer.save()
                email = serializer.validated_data['email']
                log_request(request, "Create Single Email ", "info",
                            "User created single email successfully")
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Single Email created successfully",
                    "data": {
                        "id": obj.id,
                        "email": email,
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                # activity log
                log_request(request, "Create single email ", "errors",
                            "User tried to create single email but faced an error")
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception(str(e))
            # activity log
            log_request(request, "Create Single Email", "errors",
                        "User tried to create single email  but faced an error")
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
            single_emails = SingleEmail.objects.all()
            serializer = serializers.SingleEmailViewSerializer(
                single_emails, many=True)
            log_request(request, "Retrieve Single Emails", "info",
                        "User fetched single emails successfully")
            return Response({
                "code": 200,
                "status": "success",
                "message": "Single emails retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            log_request(request, "Retrieve Single Emails", "errors",
                        "User tried to fetch single emails but faced an error")
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
            single_email = SingleEmail.objects.get(id=id)
            serializer = serializers.SingleEmailSerializer(
                single_email, data=request.data, partial=True)
            if serializer.is_valid():
                obj = serializer.save()
                log_request(request, "Update Single Email", "info",
                            "User updated single email successfully")
                return Response({
                    "code": 200,
                    "status": "success",
                    "message": "Single email updated successfully",
                    "data": {
                        "id": obj.id,
                        "email": obj.email,
                    }
                }, status=status.HTTP_200_OK)
            else:
                log_request(request, "Update Single Email", "errors",
                            f"User tried to update single email but faced an error: {serializer.errors}")
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except SingleEmail.DoesNotExist:
            log_request(request, "Update Single Email", "errors",
                        f"User tried to update single email but it does not exist")
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Single email not found",
                "errors": {
                    "id": ["Single email not found for the given id"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_request(request, "Update Single Email", "errors",
                        f"User tried to update single email but faced an error")
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
            single_email = SingleEmail.objects.get(id=id)
            single_email.delete()
            log_request(request, "Delete Single Email", "info",
                        "User deleted single email successfully")
            return Response({
                "code": 204,
                "status": "success",
                "message": "Single email deleted successfully"
            }, status=status.HTTP_204_NO_CONTENT)
        except SingleEmail.DoesNotExist:
            log_request(request, "Delete Single Email", "errors",
                        "User tried to delete single email but it does not exist")
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Single email not found",
                "errors": {
                    "id": ["Single email not found for the given id"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_request(request, "Delete Single Email", "errors",
                        f"User tried to delete single email but faced an error")
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailSendView(APIView):
    permission_classes = [IsAuthenticated, BulkEmailManagementPermission]

    def post(self, request):
        try:
            serializer = serializers.EmailSendSerializer(data=request.data)
            if serializer.is_valid():
                obj = serializer.save()
                email_compose = serializer.validated_data['email_compose']
                group = serializer.validated_data.get("group", None)
                single_email = serializer.validated_data.get(
                    "single_email", None)
                if single_email is None and group is not None:
                    bulk_email_send_task.delay_on_commit(
                        email_compose_id=email_compose.id,
                        email_addresses=list(
                            group.group_email_lists.values_list('email', flat=True))
                    )
                elif group is None and single_email is not None:
                    bulk_email_send_task.delay_on_commit(
                        email_compose_id=email_compose.id,
                        email_addresses=[single_email.email]
                    )

                # activity log
                log_request(request, "Create Email Send", "info",
                            "User created email send successfully")
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Email send created successfully",
                    "data": {
                        "id": obj.id,
                        "email_compose": obj.email_compose.id,

                    }
                }, status=status.HTTP_201_CREATED)
            else:
                log_request(request, "Create Email Send", "errors",
                            f"User tried to create email send but faced an error: {serializer.errors}")
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_request(request, "Create Email Send", "errors",
                        f"User tried to create email send but faced an error")
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OutboxView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            outbox = Outbox.objects.all()
            serializer = serializers.OutboxViewSerializer(outbox, many=True)
            log_request(request, "Retrieve Outbox", "info",
                        "User fetched outbox successfully")
            return Response({
                "code": 200,
                "status": "success",
                "message": "Outbox retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            log_request(request, "Retrieve Outbox", "errors",
                        "User tried to fetch outbox but faced an error")
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailOutboxDetailView(APIView):
    permission_classes = [IsAuthenticated, BulkEmailManagementPermission]

    def get(self, request, id):
        try:
            outbox = Outbox.objects.get(id=id)
            serializer = serializers.OutboxViewSerializer(outbox)
            log_request(request, "Retrieve Outbox Detail", "info",
                        "User fetched outbox detail successfully")
            return Response({
                "code": 200,
                "status": "success",
                "message": "Outbox detail retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Outbox.DoesNotExist:
            log_request(request, "Retrieve Outbox Detail", "errors",
                        f"User tried to fetch outbox detail but it does not exist")
            return Response({
                "code": 404,
                "status": "failed",
                "message": "Outbox not found",
                "errors": {
                    "id": ["Outbox not found for the given id"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_request(request, "Retrieve Outbox Detail", "errors",
                        f"User tried to fetch outbox detail but faced an error")
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
