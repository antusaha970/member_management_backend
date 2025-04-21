from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from .models import RestaurantCuisineCategory, RestaurantCategory, Restaurant, RestaurantItemCategory, RestaurantItem
import logging
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
from member_financial_management.models import Invoice, InvoiceItem, InvoiceType
from member_financial_management.utils.functions import generate_unique_invoice_number
from member.models import Member
from django.db import transaction
from functools import reduce
from datetime import date
from member_financial_management.serializers import InvoiceSerializer
from core.utils.pagination import CustomPageNumberPagination
from promo_code_app.models import AppliedPromoCode
from django.core.cache import cache
from django.utils.http import urlencode
import pdb
logger = logging.getLogger("myapp")


class RestaurantCuisineCategoryView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            serializer = serializers.RestaurantCuisineCategorySerializer(
                data=request.data)
            if serializer.is_valid():
                serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User created a new Restaurant cuisine category",
                )
                cache.delete_pattern("restaurant_cuisines::*")
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Cuisine category was successfully created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User tried to create a new Restaurant cuisine category but faced an error",
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
                verb="Creation",
                severity_level="info",
                description="User tried to create a new Restaurant cuisine category but faced an error",
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
            query_items = sorted(request.query_params.items())
            query_string = urlencode(query_items) if query_items else "default"
            cache_key = f"restaurant_cuisines::{query_string}"
            cached_response = cache.get(cache_key)
            if cached_response:
                return Response(cached_response, status=200)

            # Only hit DB if cache miss
            cuisines = RestaurantCuisineCategory.objects.filter(
                is_active=True).order_by("id")

            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                cuisines, request=request, view=self)
            serializer = serializers.RestaurantCuisineCategorySerializer(
                paginated_queryset, many=True)

            response_data = {
                "code": 200,
                "status": "success",
                "message": "viewing all available cuisines",
                "data": serializer.data
            }

            # Use paginator to build full response (with count, next, previous)
            final_response = paginator.get_paginated_response(response_data)

            # Cache the actual response content (final_response.data)
            cache.set(cache_key, final_response.data, timeout=60 * 30)

            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all restaurant cuisines",
            )

            return final_response

        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view all restaurant cuisines but faced an error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantCategoryView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            serializer = serializers.RestaurantCategorySerializer(
                data=request.data)
            if serializer.is_valid():
                serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User created a new restaurant category",
                )
                cache.delete_pattern("restaurant_categories::*")
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Category was successfully created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User made a bad request in Restaurant category creation API",
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
                verb="Creation",
                severity_level="info",
                description="User tried to crate Restaurant category and failed",
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
            query_items = sorted(request.query_params.items())
            query_string = urlencode(query_items) if query_items else "default"
            cache_key = f"restaurant_categories::{query_string}"
            cached_response = cache.get(cache_key)
            if cached_response:
                return Response(cached_response, status=200)

            paginator = CustomPageNumberPagination()
            categories = RestaurantCategory.objects.filter(is_active=True)
            paginated_queryset = paginator.paginate_queryset(
                categories, request=request, view=self)
            serializer = serializers.RestaurantCategorySerializer(
                paginated_queryset, many=True)
            final_response = paginator.get_paginated_response({
                "code": 200,
                "status": "success",
                "message": "viewing all available categories",
                "data": serializer.data
            }, status=200)
            cache.set(cache_key, final_response.data, timeout=60 * 30)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all restaurant categories",
            )
            return final_response
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view all restaurant categories but failed",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            query_items = sorted(request.query_params.items())
            query_string = urlencode(query_items) if query_items else "default"
            cache_key = f"restaurants::{query_string}"
            cached_response = cache.get(cache_key)
            if cached_response:
                return Response(cached_response, status=200)

            # Only hit DB if cache miss
            paginator = CustomPageNumberPagination()
            data = Restaurant.objects.select_related(
                "cuisine_type", "restaurant_type").filter(is_active=True)
            paginated_queryset = paginator.paginate_queryset(
                data, request=request, view=self)
            serializer = serializers.RestaurantViewSerializer(
                paginated_queryset, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all restaurants",
            )
            final_response = paginator.get_paginated_response({
                "code": 200,
                "status": "success",
                "message": "Viewing all available restaurant",
                "data": serializer.data
            }, status=200)
            cache.set(cache_key, final_response.data, timeout=60 * 30)
            return final_response

        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view all restaurants but failed",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            })

    def post(self, request):
        try:
            serializer = serializers.RestaurantSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User created a new restaurant",
                )
                cache.delete_pattern("restaurants::*")
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Restaurant was successfully created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User made a bad request while creating restaurant",
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
                verb="Creation",
                severity_level="info",
                description="User tried to create Restaurant and an error occurred",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantItemCategoryView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            serializer = serializers.RestaurantItemCategorySerializer(
                data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User created a new restaurant item category",
                )
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Item category was successfully created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User tried to create a new restaurant item category and made a bad request",
                )
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Creation",
                severity_level="info",
                description="User tried to create a new restaurant item category and an error occurred",
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
            cuisines = RestaurantItemCategory.objects.filter(is_active=True)
            serializer = serializers.RestaurantItemCategorySerializer(
                cuisines, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all restaurant items categories",
            )
            return Response({
                "code": 200,
                "status": "success",
                "message": "viewing all available item categories",
                "data": serializer.data
            })
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view all available item categories but failed",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantItemView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        try:
            restaurant_id = request.query_params.get("restaurant")
            if restaurant_id:
                if not Restaurant.objects.filter(id=restaurant_id).exists():
                    return Response({
                        "code": 400,
                        "status": "bad request",
                        "message": "Something want wrong",
                        "errors": {
                            "restaurant_id": ["Not restaurant exist with this id"]
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    items = RestaurantItem.objects.prefetch_related("item_media").filter(
                        restaurant__id=restaurant_id)
                    serializer = serializers.RestaurantItemForViewSerializer(
                        items, many=True)
                    log_activity_task.delay_on_commit(
                        request_data_activity_log(request),
                        verb="View",
                        severity_level="info",
                        description="User viewed all restaurant items",
                    )
                    return Response({
                        "code": 200,
                        "status": "success",
                        "message": "Viewing all restaurant items",
                        "data": serializer.data
                    })
            else:
                return Response({
                    "code": 400,
                    "status": "bad request",
                    "message": "Something want wrong",
                    "errors": {
                        "query_param": ["Missing required query parameter restaurant"]
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view all restaurant items but failed",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            serializer = serializers.RestaurantItemSerializer(data=data)
            if serializer.is_valid():
                instance = serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User created a new restaurant item",
                )
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Successfully created restaurant item",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User made a bad request",
                )
                return Response({
                    "code": 400,
                    "status": "success",
                    "message": "Something went wrong",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Creation",
                severity_level="info",
                description="User tried to create a new restaurant item but failed",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantItemMediaView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            serializer = serializers.RestaurantItemMediaSerializer(
                data=request.data)
            if serializer.is_valid():
                serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User added restaurant item media",
                )
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Restaurant item media was successfully added"
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({"code": 400,
                                 "status": "failed",
                                 "message": "Bad request",
                                 "errors": serializer.errors
                                 }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Creation",
                severity_level="info",
                description="User tried to add restaurant item media but failed",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestaurantItemBuyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = serializers.RestaurantItemBuySerializer(
                data=request.data)
            if serializer.is_valid():
                restaurant = serializer.validated_data["restaurant"]
                restaurant_items = serializer.validated_data["restaurant_items"]
                member = serializer.validated_data["member_ID"]
                member = Member.objects.get(member_ID=member)
                total_amount = reduce(
                    lambda acc, item: acc + item["id"].selling_price*item["quantity"], restaurant_items, 0)
                invoice_type, _ = InvoiceType.objects.get_or_create(
                    name="Restaurant")
                promo_code = serializer.validated_data["promo_code"]
                discount = 0
                if promo_code != None:
                    if promo_code.percentage is not None:
                        percentage = promo_code.percentage
                        discount = (percentage/100) * total_amount
                        total_amount = total_amount - discount
                    else:
                        discount = promo_code.amount
                        if discount <= total_amount:
                            total_amount = total_amount - discount
                        else:
                            discount = total_amount
                            total_amount = 0
                    promo_code.remaining_limit -= 1
                    promo_code.save(update_fields=["remaining_limit"])
                else:
                    promo_code = ""
                with transaction.atomic():
                    invoice = Invoice.objects.create(
                        currency="BDT",
                        invoice_number=generate_unique_invoice_number(),
                        balance_due=total_amount,
                        paid_amount=0,
                        issue_date=date.today(),
                        total_amount=total_amount,
                        is_full_paid=False,
                        status="unpaid",
                        invoice_type=invoice_type,
                        generated_by=request.user,
                        member=member,
                        restaurant=restaurant,
                        discount=discount,
                        promo_code=promo_code
                    )
                    if promo_code != "":
                        AppliedPromoCode.objects.create(
                            discounted_amount=discount, promo_code=promo_code, used_by=member)
                    restaurant_items_objs = []
                    for item in restaurant_items:
                        restaurant_items_objs.append(item["id"].id)
                    invoice_item = InvoiceItem.objects.create(
                        invoice=invoice
                    )
                    invoice_item.restaurant_items.set(restaurant_items_objs)
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "Invoice created successfully",
                    "data": InvoiceSerializer(invoice).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong. Please try again.",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
