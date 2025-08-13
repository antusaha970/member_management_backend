from .utils.permission_classes import ProductManagementPermission
from member_financial_management.tasks import delete_invoice_cache
from django.utils.http import urlencode
from django.core.cache import cache
import pdb
from .models import Product, Brand, ProductCategory, ProductMedia, ProductPrice
from django.shortcuts import render
from rest_framework.views import APIView
from product import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
import logging
from member.models import Member
from member_financial_management.utils.functions import generate_unique_invoice_number
from member_financial_management.models import Invoice, InvoiceItem, InvoiceType
from django.db import transaction
from datetime import date
from member_financial_management.serializers import InvoiceSerializer
from promo_code_app.models import AppliedPromoCode
from core.utils.pagination import CustomPageNumberPagination
from member_financial_management.utils.permission_classes import MemberFinancialManagementPermission
logger = logging.getLogger("myapp")
from .tasks import delete_products_cache
from .utils.filters import ProductFilter

class BrandView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), ProductManagementPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        """
        This endpoint allows you to create a new product brands  and logs an activity.
        Args:
            request (Request): The request containing the data for the new product brand instance.
        Returns:
            Response: The response containing the new product brand id and name .
        """
        try:
            data = request.data
            serializer = serializers.BrandSerializer(data=data)
            if serializer.is_valid():
                brand_instance = serializer.save()
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

    def get(self, request):
        """
        Retrieves a list of all product brands and logs an activity.
        Returns:
            Response: The response containing the list of all product brands.
        """
        try:

            brands = Brand.objects.all().order_by("id")
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

class ProductBrandDetailView(APIView):

    def patch(self, request, pk):
        try:
            brand = Brand.objects.get(pk=pk)
            serializer = serializers.BrandSerializer(brand, data=request.data, partial=True)
            if serializer.is_valid():
                obj = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Brand updated successfully",
                    severity_level="info",
                    description="Brand updated successfully"
                )
                return Response({
                    "code": 200,
                    "message": "Brand updated successfully",
                    "status": "success",
                    "data": {
                        "id": obj.id,
                        "name": obj.name
                    }
                }, status=status.HTTP_200_OK)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Brand update failed",
                    severity_level="error",
                    description="Invalid request made to update brand"
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Brand.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Brand update failed",
                severity_level="error",
                description="Brand not found for update"
            )
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Brand not found",
                "status": "failed",
                "data": {
                    "brand": ["Brand not found for provided id"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Brand update failed",
                severity_level="error",
                description="Exception occurred while updating brand"
            )
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            brand = Brand.objects.get(pk=pk)
            brand.delete()

            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Brand deleted successfully",
                severity_level="info",
                description="Brand marked as inactive"
            )
            return Response({
                "code": 204,
                "message": "Brand Soft deleted successfully",
                "status": "success"
            }, status=status.HTTP_204_NO_CONTENT)
        except Brand.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Brand delete failed",
                severity_level="error",
                description="Attempted to delete non-existent brand"
            )
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Brand not found",
                "status": "failed",
                "data": {
                    "brand": ["Brand not found for provided id"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Brand delete failed",
                severity_level="error",
                description="Exception occurred while deleting brand"
            )
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductCategoryView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), ProductManagementPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        """
        This endpoint allows you to create a new product categories and logs an activity.
        Args:
            request (Request): The request containing the data for the new product category instance.
        Returns:
            Response: The response containing the new product category id and name .
        """
        try:
            data = request.data
            serializer = serializers.ProductCategorySerializer(data=data)
            if serializer.is_valid():
                product_category_instance = serializer.save()
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

    def get(self, request):
        """
        Retrieves a list of all product categories and logs an activity.
        Returns:
            Response: The response containing the list of all product categories.
        """
        try:
            product_categories = ProductCategory.objects.all().order_by('id') 
            serializer = serializers.ProductCategoryViewSerializer(
                product_categories, many=True)
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

class ProductCategoryDetailView(APIView):
    
    def  patch(self, request, pk):
        try:
            product_category = ProductCategory.objects.get(pk=pk)
            serializer = serializers.ProductCategorySerializer(
                product_category, data=request.data, partial=True)
            if serializer.is_valid():
                obj = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Product category updated successfully",
                    severity_level="info",
                    description="Product category updated successfully")
                return Response({
                    "code": 200,
                    "message": "Product category updated successfully",
                    "status": "success",
                    "data":{
                        "id": obj.id,
                        "name": obj.name
                    }
                },status=status.HTTP_200_OK)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Category update failed",
                    severity_level="error",
                    description="user tried to update product category but made an invalid request",)
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
        except ProductCategory.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product category update failed",
                severity_level="error",
                description="An error occurred while update product category",)
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Product category not found",
                "status": "failed",
                "data":{
                    "category":["Product category not found for provided id"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product category update failed",
                severity_level="error",
                description="user tried to update product category but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def delete(self, request, pk):
        try:
            product_category = ProductCategory.objects.get(pk=pk)
            product_category.delete()
            
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product category deleted successfully",
                severity_level="info",
                description="Product category deleted successfully"
            )
            
            return Response({
                "code": 204,
                "message": "Product category deleted successfully",
                "status": "success",
               
            }, status=status.HTTP_204_NO_CONTENT)
        
        except ProductCategory.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product category delete failed",
                severity_level="error",
                description="Tried to delete non-existing product category"
            )
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Product category not found",
                "status": "failed",
                "data": {
                    "category": ["Product category not found for provided id"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product category delete failed",
                severity_level="error",
                description="An error occurred while deleting product category"
            )
        return Response({
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Error occurred",
            "status": "failed",
            "errors": {
                "server_error": [str(e)]
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    
       
class ProductView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), ProductManagementPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        """
        This endpoint allows you to create a new product and logs an activity.
        Args:
            request (Request): The request containing the data for the new product  instance.
        Returns:
            Response: The response containing the new product id and name .
        """
        try:
            data = request.data
            serializer = serializers.ProductSerializer(data=data)
            if serializer.is_valid():
                product_instance = serializer.save()
                # cache_delete
                delete_products_cache.delay()

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

                }, status=status.HTTP_201_CREATED)
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
        """
        Retrieves a list of all products  and logs an activity.
        Returns:
            Response: The response containing the list of all products.
        """
        try:
            query_items = sorted(request.query_params.items())
            query_string = urlencode(query_items) if query_items else "default"
            cache_key = f"products::{query_string}"
            cached_response = cache.get(cache_key)
            if cached_response:
                return Response(cached_response, status=200)
            products = Product.objects.filter(is_active=True).order_by('id')
            filtered = ProductFilter(request.query_params, queryset=products)
            queryset = filtered.qs  # Apply filters
            # Apply pagination
            paginator = CustomPageNumberPagination()
            paginated_products = paginator.paginate_queryset(
                queryset, request, view=self)
            serializer = serializers.ProductViewSerializer(
                paginated_products, many=True)
            # activity log
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Products retrieval successful",
                severity_level="info",
                description="User successfully retrieved all products",)
            final_response = paginator.get_paginated_response({
                "code": 200,
                "message": "Product list retrieved successfully",
                "status": "success",
                "data": serializer.data,
            })
            # Cache the response
            cache.set(cache_key, final_response.data,
                      timeout=60 * 30)  # Cache for 30 minutes
            return final_response
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
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), ProductManagementPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        """
        This endpoint allows you to create a new product media and logs an activity.
        Args:
            request (Request): The request containing the data for the new product media instance.
        Returns:
            Response: The response containing the new product media instance id .
        """
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
                # delete products cache
                delete_products_cache.delay()
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
    def get(self, request):
        """
        Retrieves a list of all product media and logs an activity.
        Returns:
            Response: The response containing the list of all product media.
        """
        try:
           
            product_media = ProductMedia.objects.filter(is_active=True).select_related('product').order_by('id')
            # Apply pagination
            paginator = CustomPageNumberPagination()
            paginated_media = paginator.paginate_queryset(product_media, request, view=self)
            serializer = serializers.ProductMediaViewSerializer(paginated_media, many=True)
            # activity log
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product media retrieval successful",
                severity_level="info",
                description="User successfully retrieved all product media"
            )
            final_response = paginator.get_paginated_response({
                "code": 200,
                "message": "Product media list retrieved successfully",
                "status": "success",
                "data": serializer.data,
            })
            return final_response
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product media retrieval failed",
                severity_level="error",
                description="An error occurred while retrieving product media"
            )
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class ProductPriceView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), ProductManagementPermission()]
        else:
            return [IsAuthenticated()]

    def post(self, request):
        """
        Creates a new product price instance and logs an activity.
        Args:
            request (Request): The request containing the data for the new product price instance.
        Returns:
            Response: The response containing the new product price instance's id and price.
        """
        try:
            data = request.data
            serializer = serializers.ProductPriceSerializer(data=data)
            if serializer.is_valid():
                product_price_instance = serializer.save()
                # cache_delete
                delete_products_cache.delay()
                product_price = serializer.validated_data["price"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Product price created successfully",
                    severity_level="info",
                    description="Product price created successfully ")
                return Response({
                    "code": 201,
                    "message": "Product price created successfully ",
                    "status": "success",
                    "data": {
                        "id": product_price_instance.id,
                        "price": product_price,

                    }

                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Product price creation failed",
                    severity_level="error",
                    description="user tried to create a new product price but made an invalid request",)
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
                verb="Product price creation failed",
                severity_level="error",
                description="user tried to create a new product price but made an invalid request",)
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
        Retrieves a list of all product prices and logs an activity.
        Returns:
            Response: The response containing the list of product prices.
        """
        try:
            
            price = ProductPrice.objects.filter(is_active=True).select_related(
                'product', 'membership_type').order_by('id')
            # Apply pagination
            paginator = CustomPageNumberPagination()
            paginated_price = paginator.paginate_queryset(
                price, request, view=self)
            serializer = serializers.ProductPriceViewSerializer(
                paginated_price, many=True)
            # activity log
            log_activity_task.delay_on_commit(

                request_data_activity_log(request),
                verb="Product price retrieval successful",
                severity_level="info",
                description="User successfully retrieved all product prices"
            )
            final_response = paginator.get_paginated_response({
                "code": 200,
                "message": "Product price list retrieved successfully",
                "status": "success",
                "data": serializer.data,

            })
            
            return final_response
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product price retrieval failed",
                severity_level="error",
                description="An error occurred while retrieving product price for product",)
            return Response({

                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), ProductManagementPermission()]
        else:
            return [IsAuthenticated()]

    def get(self, request, product_id):
        """
        Retrieves a specific product by its product_id and logs an activity.
        Args:
            request (Request): The request object.
            product_id (int): The product_id of the product to retrieve.
        Returns:
            Response: The response containing the product details.
        """
        try:
            cache_key = f"product_details::{product_id}"
            cached_response = cache.get(cache_key)
            if cached_response:
                return Response(cached_response, status=200)
            product = Product.objects.select_related(
                'category', 'brand').prefetch_related('product_media').get(id=product_id)
            serializer = serializers.SpecificProductViewSerializer(product)
            log_activity_task.delay_on_commit(

                request_data_activity_log(request),
                verb="Product details retrieved successfully",
                severity_level="info",
                description="User successfully retrieved specific product details"
            )
            final_response = Response({

                "code": 200,
                "message": "Product details retrieved successfully",
                "status": "success",
                "data": serializer.data,

            }, status=status.HTTP_200_OK)
            # Cache the response
            cache.set(cache_key, final_response.data,
                      timeout=60 * 30)  # Cache for 30 minutes
            return final_response
        except Product.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product details retrieval failed",
                severity_level="error",
                description="An error occurred while retrieving product details for product",)
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Product not found",
                "status": "failed",
                "errors": {
                    "product": ["Product not found"]
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Product details retrieval failed",
                severity_level="error",
                description="An error occurred while retrieving product details for product",)
            return Response({

                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductBuyView(APIView):
    permission_classes = [IsAuthenticated, MemberFinancialManagementPermission]

    def post(self, request):
        """
        Creates an invoice for a product purchase.
        Args:
            request (Request): The request containing the data for the invoice instance.
        Returns:
            Response: The response containing the created invoice and a success message.
        """
        try:
            data = request.data
            serializer = serializers.ProductBuySerializer(data=data)

            if serializer.is_valid():
                member_id = serializer.validated_data["member_ID"]
                product_items = serializer.validated_data["product_items"]
                member = Member.objects.get(member_ID=member_id)
                promo_code = serializer.validated_data["promo_code"]
                discount = 0
                total_price = 0
                product_ids = []
                for item in product_items:
                    product = item["product"]
                    quantity = item["quantity"]
                    product_price = ProductPrice.objects.filter(
                        product=product, membership_type=member.membership_type).first()
                    if product_price:
                        total_price += product_price.price * quantity
                    else:
                        total_price += product.price * quantity
                    product_ids.extend([product.id] * quantity)
                if promo_code is not None:
                    if promo_code.percentage is not None:
                        percentage = promo_code.percentage
                        discount = (percentage/100) * total_price
                        total_price = total_price - discount
                    else:
                        discount = promo_code.amount
                        if discount <= total_price:
                            total_price = total_price - discount
                        else:
                            discount = total_price
                            total_price = 0
                    promo_code.remaining_limit -= 1
                    promo_code.save(update_fields=["remaining_limit"])
                else:
                    promo_code = ""
                invoice_type, _ = InvoiceType.objects.get_or_create(
                    name="Product")
                with transaction.atomic():

                    invoice = Invoice.objects.create(
                        currency="BDT",
                        invoice_number=generate_unique_invoice_number(),
                        balance_due=total_price,
                        paid_amount=0,
                        issue_date=date.today(),
                        total_amount=total_price,
                        is_full_paid=False,
                        status="unpaid",
                        invoice_type=invoice_type,
                        generated_by=request.user,
                        member=member,
                        promo_code=promo_code,
                        discount=discount,
                    )

                    if promo_code != "":
                        AppliedPromoCode.objects.create(
                            discounted_amount=discount, promo_code=promo_code, used_by=member)
                    invoice_item = InvoiceItem.objects.create(invoice=invoice)
                    invoice_item.products.set(product_ids)

                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Invoice created successfully",
                    severity_level="info",
                    description="User generated an invoice successfully",
                )
                # Delete cache for invoice
                delete_invoice_cache.delay()

                return Response({
                    "code": 200,
                    "message": "Invoice created successfully",
                    "status": "success",
                    "data": InvoiceSerializer(invoice).data
                }, status=status.HTTP_200_OK)

            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Invoice creation failed",
                    severity_level="error",
                    description="User attempted to generate an invoice with invalid data",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Invalid request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "code": 500,
                "status": "error",
                "message": "Something went wrong",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
