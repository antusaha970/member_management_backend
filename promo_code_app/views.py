
import pdb
from django.shortcuts import render

# Create your views here.
from .models import AppliedPromoCode, PromoCode, PromoCodeCategory
from django.shortcuts import render
from rest_framework.views import APIView
from promo_code_app import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from activity_log.tasks import  log_activity_task
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from activity_log.tasks import get_location, get_client_ip, log_activity_task
from activity_log.utils.functions import request_data_activity_log
import logging
logger = logging.getLogger("myapp")


class PromoCodeCategoryView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    
    def post(self,request):
        """
        This endpoint allows you to create a new promo codes and logs an activity.
        Args:
            request (Request): The request containing the data for the new promo code instance.
        Returns:
            Response: The response containing the new promo code category id and name .
        """
        try:
            data = request.data
            serializer = serializers.PromoCodeCategorySerializer(data=data)
            if serializer.is_valid():
                promo_code_instance = serializer.save()
                promo_code_name = serializer.validated_data["name"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Promo code created successfully",
                    severity_level="info",
                    description="Promo code created successfully",)
                return Response({
                    "code": 201,
                    "message": "Promo code category created successfully",
                    "status": "success",
                    "data": {
                        "id": promo_code_instance.id,
                        "name": promo_code_name,

                    }
                })
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Promo code creation failed",
                    severity_level="error",
                    description="user tried to create a new promo code category but made an invalid request",)
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
                verb="Promo code creation failed",
                severity_level="error",
                description="user tried to create a new promo code category but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """
        Retrieves a list of all product categories and logs an activity.
        Returns:
            Response: The response containing the list of all product categories.
        """
        try:
            promo_code_categories = PromoCodeCategory.objects.all()
            serializer = serializers.PromoCodeCategoryViewSerializer(
                promo_code_categories, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Promo code category retrieval successful",
                severity_level="info",
                description="User successfully retrieved all promo code categories",)
            return Response({
                "code": 200,
                "message": "Promo code category list retrieved successfully",
                "status": "success",
                "data": serializer.data,
            })
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Promo code category retrieval failed",
                severity_level="error",
                description="An error occurred while retrieving all promo code categories",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PromoCodeView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        """
        This endpoint allows you to create a new promo code and logs an activity.
        Args:
            request (Request): The request containing the data for the new promo code instance.
        Returns:
            Response: The response containing the new promo code id and name.
        """
        try:
            data = request.data
            serializer = serializers.PromoCodeSerializer(data=data)
            if serializer.is_valid():
                promo_code_instance = serializer.save()
                promo_code = serializer.validated_data["promo_code"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Promo code created successfully",
                    severity_level="info",
                    description="Promo code created successfully",)
                return Response({
                    "code": 201,
                    "message": "Promo code created successfully",
                    "status": "success",
                    "data": {
                        "id": promo_code_instance.id,
                        "promo_code": promo_code,

                    }
                })
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Promo code creation failed",
                    severity_level="error",
                    description="user tried to create a new promo code but made an invalid request",)
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
                verb="Promo code creation failed",
                severity_level="error",
                description="user tried to create a new promo code but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """
        Retrieves a list of all promo codes and logs an activity.
        Returns:
            Response: The response containing the list of all promo codes.
        """
        try:
            promo_codes = PromoCode.objects.filter(is_active=True)
            serializer = serializers.PromoCodeDetailViewSerializer(
                promo_codes, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Promo code retrieval successful",
                severity_level="info",
                description="User successfully retrieved all promo codes",)
            return Response({
                "code": 200,
                "message": "Promo code list retrieved successfully",
                "status": "success",
                "data": serializer.data,
            })
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Promo code retrieval failed",
                severity_level="error",
                description="An error occurred while retrieving all promo codes",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AppliedPromoCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = AppliedPromoCode.objects.filter(is_active=True)
            serializer = serializers.AppliedPromoCodeSerializer(
                data, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="error",
                description="User viewed the list of all applied promo codes.")
            return Response({
                "code": 200,
                "status": "success",
                "message": "List of all applied promo code",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Promo code category retrieval failed",
                severity_level="error",
                description="An error occurred while retrieving all promo code categories")
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
