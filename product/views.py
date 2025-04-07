from .models import Product,Brand,ProductCategory,ProductMedia,ProductPrice
from django.shortcuts import render
from rest_framework.views import APIView
from product import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from activity_log.tasks import get_location, get_client_ip, log_activity_task
from activity_log.utils.functions import request_data_activity_log
import logging
logger = logging.getLogger("myapp")
import pdb

          
class BrandView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def post(self,request):
        try:
            data = request.data
            serializer = serializers.BrandSerializer(data=data)
            if serializer.is_valid():
                brand_instance=serializer.save()
                brand_name = serializer.validated_data["name"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Brand created successfully",
                    severity_level="info",
                    description="Brand created successfully for a new product",)
                return Response({
                        "code": 201,
                        "message": "Brand created successfully for product",
                        "status": "success",
                        "data": {
                            "id": brand_instance.id,
                            "name": brand_name,
                            
                        }
                })
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Brand creation failed",
                    severity_level="error",
                    description="user tried to create a new brand but made an invalid request",)
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
                verb="Brand creation failed",
                severity_level="error",
                description="user tried to create a new brand but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self,request):
        try:
            brands = Brand.objects.all()
            serializer = serializers.BrandViewSerializer(brands, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Brand retrieval successful",
                severity_level="info",
                description="User successfully retrieved all brands",)
            return Response({
                "code": 200,
                "message": "Brand list retrieved successfully",
                "status": "success",
                "data": serializer.data,
            })
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Brand retrieval failed",
                severity_level="error",
                description="An error occurred while retrieving all brands",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class ProductCategoryView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    
    def post(self,request):
        try:
            data = request.data
            serializer = serializers.ProductCategorySerializer(data=data)
            if serializer.is_valid():
                product_category_instance=serializer.save()
                product_category_name = serializer.validated_data["name"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Product category created successfully",
                    severity_level="info",
                    description="Product category created successfully for a new product",)
                return Response({
                        "code": 201,
                        "message": "Product category created successfully for product",
                        "status": "success",
                        "data": {
                            "id": product_category_instance.id,
                            "name": product_category_name,
                            
                        }
                })
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Product category creation failed",
                    severity_level="error",
                    description="user tried to create a new product category but made an invalid request",)
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
                verb="Product category creation failed",
                severity_level="error",
                description="user tried to create a new product category but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def get(self,request):
        try:
            product_categories = ProductCategory.objects.all()
            serializer = serializers.ProductCategoryViewSerializer(product_categories, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product category retrieval successful",
                severity_level="info",
                description="User successfully retrieved all product categories",)
            return Response({
                "code": 200,
                "message": "Product category list retrieved successfully",
                "status": "success",
                "data": serializer.data,
            })
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product category retrieval failed",
                severity_level="error",
                description="An error occurred while retrieving all product categories",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
class ProductView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    
    def post(self, request):
        try:
            data = request.data
            serializer = serializers.ProductSerializer(data=data)
            if serializer.is_valid():
                product_instance=serializer.save()
                product_name = serializer.validated_data["name"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Product created successfully",
                    severity_level="info",
                    description="Product created successfully ",)
                return Response({
                        "code": 201,
                        "message": "Product created successfully ",
                        "status": "success",
                        "data": {
                            "id": product_instance.id,
                            "name": product_name,
                           
                        }
                        
                },status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Product creation failed",
                    severity_level="error",
                    description="user tried to create a new product but made an invalid request",)
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
                verb="Product creation failed",
                severity_level="error",
                description="user tried to create a new product but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        try:
            products = Product.objects.all()
            serializer = serializers.ProductViewSerializer(products, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Products retrieval successful",
                severity_level="info",
                description="User successfully retrieved all products",)
            return Response({
                "code": 200,
                "message": "Product list retrieved successfully",
                "status": "success",
                "data": serializer.data,
            })
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product retrieval failed",
                severity_level="error",
                description="An error occurred while retrieving all products",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)                 
                            
class ProductMediaView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    
    def post(self, request):
        try:
            data = request.data
            serializer = serializers.ProductMediaSerializer(data=data)
            if serializer.is_valid():
                media_instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Product media created successfully",
                    severity_level="info",
                    description="Product media created successfully for product",)
                return Response({
                        "code": 201,
                        "message": "Product media created successfully",
                        "status": "success",
                        "data": {
                            "image_id": media_instance.id,
                            
                        }
                        }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Product media creation failed",
                    severity_level="error",
                    description="user tried to create a new product media but made an invalid request",)
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
                verb="Product media creation failed",
                severity_level="error",
                description="user tried to create a new product media but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self,request):
        try :
            media = ProductMedia.objects.filter(is_active=True)
            serializer = serializers.ProductMediaViewSerializer(media, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product media retrieval successful",
                severity_level="info",
                description="User successfully retrieved product media for product",)
            return Response({
                "code": 200,
                "message": "Product media list retrieved successfully",
                "status": "success",
                "data": serializer.data,
            })
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product media retrieval failed",
                severity_level="error",
                description="An error occurred while retrieving product media for product",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        
        
               
            