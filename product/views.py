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
from member.models import Member
from member_financial_management.utils.functions import generate_unique_invoice_number
from member_financial_management.models import Invoice, InvoiceItem, InvoiceType
from django.db import transaction
from datetime import date
from member_financial_management.serializers import InvoiceSerializer

logger = logging.getLogger("myapp")
import pdb

          
class BrandView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    def post(self,request):
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
        """
        Retrieves a list of all product brands and logs an activity.
        Returns:
            Response: The response containing the list of all product brands.
        """
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
        """
        Retrieves a list of all product categories and logs an activity.
        Returns:
            Response: The response containing the list of all product categories.
        """
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
        """
        Retrieves a list of all products  and logs an activity.
        Returns:
            Response: The response containing the list of all products.
        """
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
        """
        Retrieves a list of all product media and logs an activity.
        Returns:
            Response: The response containing the list of all product media.
        """
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

class ProductPriceView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
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
                product_price_instance=serializer.save()
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
                        
                },status=status.HTTP_201_CREATED)
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
    
    def get(self,request):
        """
        Retrieves a list of all product prices and logs an activity.
        Returns:
            Response: The response containing the list of product prices.
        """
        try:
            price = ProductPrice.objects.filter(is_active=True)
            serializer = serializers.ProductPriceViewSerializer(price, many=True)
            log_activity_task.delay_on_commit(
                
                request_data_activity_log(request),
                verb="Product price retrieval successful",
                severity_level="info",
                description="User successfully retrieved all product prices"
                )
            return Response({
                "code": 200,
                "message": "Product price list retrieved successfully",
                "status": "success",
                "data": serializer.data,
                
            })
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
    permission_classes = [IsAuthenticated,IsAdminUser]
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
            product = Product.objects.get(id=product_id)
            serializer = serializers.ProductViewSerializer(product)
            log_activity_task.delay_on_commit(
                
                request_data_activity_log(request),
                verb="Product details retrieved successfully",
                severity_level="info",
                description="User successfully retrieved specific product details"
                )
            return Response({
                
                "code": 200,
                "message": "Product details retrieved successfully",
                "status": "success",
                "data": serializer.data,
                
            }, status=status.HTTP_200_OK)
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
            
class EventTicketBuyView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """
        Creates an invoice for an event ticket purchase.
        Args:
            request (Request): The request containing the data for the invoice instance.
        Returns:
            Response: The response containing the created invoice and a success message.
        """
        try:
            data = request.data
            serializer = serializers.EventTicketBuySerializer(data=data)
            if serializer.is_valid():
                
                member = serializer.validated_data["member_ID"]
                member = Member.objects.get(member_ID=member)
                event_ticket = serializer.validated_data["event_ticket"]
                
                invoice_type, _ = InvoiceType.objects.get_or_create(
                    name="Event")

                with transaction.atomic():
                    invoice = Invoice.objects.create(
                        currency="BDT",
                        invoice_number=generate_unique_invoice_number(),
                        balance_due=event_ticket.price,
                        paid_amount=0,
                        issue_date=date.today(),
                        total_amount=event_ticket.price,
                        is_full_paid=False,
                        status="unpaid",
                        invoice_type=invoice_type,
                        generated_by=request.user,
                        member=member,
                        event=event_ticket.event,
                    )
                    invoice_item = InvoiceItem.objects.create(
                        invoice=invoice
                    )
                    invoice_item.event_tickets.set([event_ticket.id])    
                    
                
                
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Invoice created successfully",
                    severity_level="info",
                    description="user generated an invoice successfully",)
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
                    description="user tried to generate an invoice but made an invalid request",)
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
                verb="Invoice creation failed",
                severity_level="error",
                description="user tried to generate an invoice but made an invalid request",)
            return Response({

                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
class ProductBuyView(APIView):
    permission_classes = [IsAuthenticated]
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
                invoice_type, _ = InvoiceType.objects.get_or_create(name="Product")

                total_price = 0
                product_ids = []

                with transaction.atomic():
                    # Calculate total price
                    for item in product_items:
                        product = item["product"]
                        quantity = item["quantity"]
                        total_price += product.price * quantity
                        product_ids.extend([product.id] * quantity)

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
                    )

                    invoice_item = InvoiceItem.objects.create(invoice=invoice)
                    invoice_item.products.set(product_ids)

                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Invoice created successfully",
                    severity_level="info",
                    description="User generated an invoice successfully",
                )

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

                   
                
            
                            
        
                     
        
           
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        
        
        
        
        
    
    
    
    
    
    
    
    
    
    
    
         
        
        
        
               
            