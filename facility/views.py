
import pdb
from django.shortcuts import render
from rest_framework.views import APIView
from facility import serializers
from rest_framework.response import Response
from rest_framework import status
from .models import Facility, FacilityUseFee
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
from member_financial_management.utils.functions import generate_unique_invoice_number
from member.models import Member
from django.db import transaction
from member_financial_management.serializers import InvoiceSerializer
from member_financial_management.models import Invoice, InvoiceItem, InvoiceType
from core.utils.pagination import CustomPageNumberPagination
from datetime import date
import logging
from django.db.models import Prefetch
from decimal import Decimal
from promo_code_app.models import AppliedPromoCode
from core.utils.pagination import CustomPageNumberPagination
from django.core.cache import cache
from django.utils.http import urlencode
from django.db.models import Q
from .filters import FacilityFilter
from .utils.permission_classes import FacilityManagementPermission
from member_financial_management.utils.permission_classes import MemberFinancialManagementPermission
from member_financial_management.tasks import delete_invoice_cache


logger = logging.getLogger("myapp")


class FacilityView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), FacilityManagementPermission()]
        else:
            return [FacilityManagementPermission()]

    def post(self, request):
        """
        Creates a new facility instance and logs an activity.
        Args:
            request (Request): The request containing the data for the new facility instance.
        Returns:
            Response: The response containing the new facility instance's id and name
        """
        try:
            data = request.data
            serializer = serializers.FacilitySerializer(data=data)
            if serializer.is_valid():
                facility_instance = serializer.save()
                # delete the cache for the facility list
                cache.delete_pattern("facilities::*")
                facility_name = serializer.validated_data["name"]
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Facility created successfully",
                    severity_level="info",
                    description="Facility created successfully",)
                return Response({
                    "code": 201,
                    "message": "Facility created successfully",
                    "status": "success",
                    "data": {
                        "facility_id": facility_instance.id,
                        "facility_name": facility_name,
                    }
                })
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Facility creation failed",
                    severity_level="error",
                    description="user tried to create a new facility but made an invalid request",)
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
                verb="Facility creation failed",
                severity_level="error",
                description="user tried to create a new facility but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            # Build cache key
            query_params = request.query_params
            query_items = sorted(query_params.items())
            query_string = urlencode(query_items) if query_items else "default"
            cache_key = f"facilities::{query_string}"

            # Check cache
            cached_response = cache.get(cache_key)
            if cached_response:
                return Response(cached_response, status=200)

            # Filtering using FacilityFilter
            base_queryset = Facility.objects.filter(
                is_active=True).order_by("id")
            filtered_qs = FacilityFilter(
                query_params, queryset=base_queryset).qs

            # Pagination
            paginator = CustomPageNumberPagination()
            paginated_qs = paginator.paginate_queryset(
                filtered_qs, request, view=self)
            serializer = serializers.FacilityViewSerializer(
                paginated_qs, many=True)

            # Final response
            response_data = {
                "code": 200,
                "message": "Facilities retrieved successfully",
                "status": "success",
                "data": serializer.data
            }
            final_response = paginator.get_paginated_response(response_data)
            # Cache the response
            cache.set(cache_key, final_response.data,
                      timeout=60 * 30)  # 30 minutes

            # Log the activity
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve all facilities",
                severity_level="info",
                description="User retrieved all facilities successfully",
            )

            return final_response

        except Exception as e:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve facilities failed",
                severity_level="error",
                description="An error occurred while retrieving facilities",
            )
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An error occurred while retrieving facilities",
                "status": "failed"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FacilityUseFeeView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), FacilityManagementPermission()]
        else:
            return [FacilityManagementPermission()]

    def post(self, request):
        """
        Creates a new facility use fee instance and logs an activity.
        Args:
            request (Request): The request containing the data for the new facility use fee instance.
        Returns:
            Response: The response containing the new facility use fee instance's id and fee
        """
        try:
            data = request.data
            serializer = serializers.FacilityUseFeeSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    facility_use_fee_instance = serializer.save()
                    # delete the cache for the facility use fees
                    cache.delete_pattern("facility_use_fees::*")
                    facility_use_fee_id = facility_use_fee_instance.id
                    facility_use_fee = facility_use_fee_instance.fee
                    log_activity_task.delay_on_commit(
                        request_data_activity_log(request),
                        verb="Facility use fee created successfully",
                        severity_level="info",
                        description="Facility use fee created successfully",)
                    return Response({
                        "code": 201,
                        "message": "Facility use fee created successfully",
                        "status": "success",
                        "data": {
                            "facility_use_fee_id": facility_use_fee_id,
                            "facility_use_fee": facility_use_fee,
                        }
                    })
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Facility use fee creation failed",
                    severity_level="error",
                    description="user tried to create a new facility use fee but made an invalid request",)
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
                verb="Facility use fee creation failed",
                severity_level="error",
                description="user tried to create a new facility use fee but made an invalid request",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """
        Retrieves a list of all facility use fees and logs an activity.
        Returns:
            Response: The response containing the list of facility use fees.
        """
        try:
            query_params = request.query_params
            query_items = sorted(query_params.items())
            query_string = urlencode(query_items) if query_items else "default"
            cache_key = f"facility_use_fees::{query_string}"
            # Check cache
            cached_response = cache.get(cache_key)
            if cached_response:
                return Response(cached_response, status=status.HTTP_200_OK)

            facility_use_fees = FacilityUseFee.objects.filter(
                is_active=True).select_related('membership_type', 'facility').order_by('id')
            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                facility_use_fees, request, view=self)
            serializer = serializers.FacilityUseFeeViewSerializer(
                paginated_queryset, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve all facility use fees",
                severity_level="info",
                description="User retrieved all facility use fees successfully",)
            final_response = paginator.get_paginated_response({
                "code": 200,
                "message": "Facility use fees retrieved successfully",
                "status": "success",
                "data": serializer.data
            })

            cache.set(cache_key, final_response.data,
                      timeout=60 * 30)  # 30 minutes
            return final_response

        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Facility use fees retrieve failed",
                severity_level="error",
                description="Error occurred while retrieving all facility use fees",)
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Error occurred",
                "status": "failed",
                'errors': {
                    'server_error': [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FacilityBuyView(APIView):
    permission_classes = [IsAuthenticated, MemberFinancialManagementPermission]

    def post(self, request):
        """
        Creates an invoice for a facility purchase.
        Args:
            request (Request): The request containing the data for the invoice instance.
        Returns:
            Response: The response containing the created invoice and a success message.
        """
        try:
            data = request.data
            serializer = serializers.FacilityBuySerializer(data=data)
            if serializer.is_valid():
                member = serializer.validated_data["member_ID"]
                member = Member.objects.get(member_ID=member)
                facility = serializer.validated_data["facility"]
                promo_code = serializer.validated_data["promo_code"]
                facility_uses_fee = FacilityUseFee.objects.filter(
                    facility=facility, membership_type=member.membership_type).first()
                fee = 0
                if facility_uses_fee:
                    fee = facility_uses_fee.fee
                else:
                    fee = facility.usages_fee
                # pdb.set_trace()

                discount = 0
                total_amount = fee
                if promo_code is not None:
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
                invoice_type, _ = InvoiceType.objects.get_or_create(
                    name="Facility")

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
                        promo_code=promo_code,
                        discount=discount
                    )
                    if promo_code != "":
                        AppliedPromoCode.objects.create(
                            discounted_amount=discount, promo_code=promo_code, used_by=member)
                    invoice_item = InvoiceItem.objects.create(
                        invoice=invoice
                    )
                    invoice_item.facility.set([facility.id])
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Invoice created successfully",
                    severity_level="info",
                    description="user generated an invoice successfully",)
                # delete the cache for the invoice list
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


class FacilityDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), FacilityManagementPermission()]
        else:
            return [FacilityManagementPermission()]

    def get(self, request, facility_id):
        try:
            cache_key = f"facility_details::{facility_id}"
            cached_response = cache.get(cache_key)
            if cached_response:
                return Response(cached_response, status=200)
            facility = Facility.objects.prefetch_related(
                Prefetch(
                    'facility_use_fees',
                    queryset=FacilityUseFee.objects.select_related(
                        'membership_type')
                )
            ).get(pk=facility_id)

            # Serialize the Facility data
            facility_serializer = serializers.SpecificFacilityDetailSerializer(
                facility)

            # Log the activity
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Retrieve a facility",
                severity_level="info",
                description="User retrieved a facility successfully",
            )

            final_response = Response({
                "code": 200,
                "message": "Facility retrieved successfully",
                "status": "success",
                "data": facility_serializer.data
            }, status=status.HTTP_200_OK)
            # Cache the response
            cache.set(cache_key, final_response.data,
                      timeout=60 * 30)  # 30 minutes
            return final_response

        except Facility.DoesNotExist:
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Facility details retrieval failed",
                severity_level="error",
                description="An error occurred while retrieving facility details",
            )
            return Response({
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Facility not found",
                "status": "failed",
                "errors": {
                    "facility": ["Facility not found"]
                }
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Facility retrieve failed",
                severity_level="error",
                description="Error occurred while retrieving a facility",
            )
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Something went wrong",
                "status": "failed",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
