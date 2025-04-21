from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
from django.db import transaction
from datetime import date
from django.db.models import Prefetch
import pdb
from core.utils.pagination import CustomPageNumberPagination
from django.shortcuts import get_object_or_404
from .models import PaymentMethod, Transaction, Payment, Sale, SaleType, IncomeParticular, IncomeReceivingOption, Income, IncomeReceivingType, MemberAccount, Due, MemberDue, Invoice
from django.utils.http import urlencode
from . import serializers
from .utils.functions import generate_unique_sale_number
logger = logging.getLogger("myapp")


class PaymentMethodView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Cache check
            data = cache.get("active_payment_methods")
            if not data:
                payment_methods = PaymentMethod.objects.filter(is_active=True)
                serializer = serializers.PaymentMethodSerializer(
                    payment_methods, many=True)
                data = serializer.data
                cache.set("active_payment_methods", data, 60 * 30)

            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all payment methods.",
            )

            return Response({
                "code": 200,
                "status": "success",
                "message": "Viewing all payment methods",
                "data": data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="error",
                description="User tried to view payment methods but faced error.",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong.",
                "errors": [str(e)]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = serializers.PaymentMethodSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                # Invalidate cache delete
                cache.delete("active_payment_methods")
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User created a new payment method",
                )

                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "New payment method has been created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="warning",
                    description="User tried to create a new payment method but faced validation error.",
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
                severity_level="error",
                description="User tried to create a new payment method but faced error.",
            )

            return Response({
                "code": 500,
                "status": "failed",
                "message": "Error while creating payment method.",
                "errors": {
                    "server_errors": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvoicePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = serializers.InvoicePaymentSerializer(
                data=request.data)
            if serializer.is_valid():
                invoice = serializer.validated_data["invoice_id"]
                payment_method = serializer.validated_data["payment_method"]
                amount = serializer.validated_data["amount"]
                income_particular = serializer.validated_data["income_particular"]
                received_from = serializer.validated_data["received_from"]
                adjust_from_balance = serializer.validated_data["adjust_from_balance"]
                with transaction.atomic():
                    if amount == invoice.total_amount:
                        invoice.paid_amount = invoice.total_amount
                        invoice.is_full_paid = True
                        invoice.status = "paid"
                        invoice.balance_due = 0
                        invoice.save(update_fields=[
                            "paid_amount", "is_full_paid", "status", "balance_due"])
                        full_receiving_type, _ = IncomeReceivingType.objects.get_or_create(
                            name="full")
                        transaction_obj = Transaction.objects.create(
                            amount=invoice.paid_amount,
                            transaction_date=date.today(),
                            status="paid",
                            member=invoice.member,
                            invoice=invoice,
                            payment_method=payment_method
                        )
                        Payment.objects.create(
                            payment_amount=invoice.paid_amount,
                            payment_status="paid",
                            payment_date=date.today(),
                            invoice=invoice,
                            member=invoice.member,
                            payment_method=payment_method,
                            processed_by=request.user,
                            transaction=transaction_obj
                        )
                        sale_type, _ = SaleType.objects.get_or_create(
                            name=invoice.invoice_type.name)
                        sale_obj = Sale.objects.create(
                            sale_number=generate_unique_sale_number(),
                            sub_total=invoice.total_amount,
                            total_amount=invoice.paid_amount,
                            payment_status="paid",
                            sale_source_type=sale_type,
                            customer=invoice.member,
                            payment_method=payment_method,
                            invoice=invoice
                        )
                        Income.objects.create(
                            receivable_amount=invoice.total_amount,
                            final_receivable=sale_obj.total_amount,
                            actual_received=invoice.paid_amount,
                            reaming_due=0,
                            particular=income_particular,
                            received_from_type=received_from,
                            receiving_type=full_receiving_type,
                            member=invoice.member,
                            received_by=payment_method,
                            sale=sale_obj,
                            discounted_amount=invoice.discount,
                            discount_name=invoice.promo_code
                        )
                        return Response(
                            {
                                "code": 200,
                                "status": "success",
                                "message": "Invoice payment successful",
                                "data": {
                                    "invoice_id": invoice.id
                                }
                            }, status=status.HTTP_200_OK
                        )
                    elif amount < invoice.total_amount and amount != 0:
                        payment_amount = amount
                        if adjust_from_balance:
                            member_account = MemberAccount.objects.get(
                                member=invoice.member)
                            member_account_balance = member_account.balance
                            remaining_payment = invoice.total_amount - payment_amount
                            if member_account_balance >= remaining_payment:
                                payment_amount = amount + remaining_payment
                                member_account.balance = member_account.balance - remaining_payment
                                member_account.save(update_fields=["balance"])
                            else:
                                payment_amount = amount + member_account_balance
                                member_account.balance = 0
                                member_account.save(update_fields=["balance"])

                        invoice.paid_amount = payment_amount
                        if invoice.paid_amount == invoice.total_amount:
                            invoice.is_full_paid = True
                            invoice.status = "paid"
                            invoice.balance_due = 0
                        else:
                            invoice.is_full_paid = False
                            invoice.status = "partial_paid"
                            invoice.balance_due = invoice.total_amount - invoice.paid_amount
                        invoice_full_paid = invoice.is_full_paid
                        invoice_status = invoice.status
                        invoice_due = invoice.balance_due
                        invoice.save(update_fields=[
                            "paid_amount", "is_full_paid", "status", "balance_due"])
                        if invoice_full_paid:
                            full_receiving_type, _ = IncomeReceivingType.objects.get_or_create(
                                name="full")
                        else:
                            full_receiving_type, _ = IncomeReceivingType.objects.get_or_create(
                                name="partial")
                        transaction_obj = Transaction.objects.create(
                            amount=amount,
                            transaction_date=date.today(),
                            status=invoice_status,
                            member=invoice.member,
                            invoice=invoice,
                            payment_method=payment_method
                        )
                        payment_obj = Payment.objects.create(
                            payment_amount=amount,
                            payment_status=invoice_status,
                            payment_date=date.today(),
                            invoice=invoice,
                            member=invoice.member,
                            payment_method=payment_method,
                            processed_by=request.user,
                            transaction=transaction_obj
                        )
                        sale_type, _ = SaleType.objects.get_or_create(
                            name=invoice.invoice_type.name)
                        sale_obj = Sale.objects.create(
                            sale_number=generate_unique_sale_number(),
                            sub_total=invoice.total_amount,
                            total_amount=invoice.paid_amount,
                            payment_status=invoice_status,
                            sale_source_type=sale_type,
                            customer=invoice.member,
                            payment_method=payment_method,
                            invoice=invoice,
                            due_date=date.today()
                        )
                        Income.objects.create(
                            receivable_amount=invoice.total_amount,
                            final_receivable=sale_obj.total_amount,
                            actual_received=amount,
                            reaming_due=invoice_due,
                            particular=income_particular,
                            received_from_type=received_from,
                            receiving_type=full_receiving_type,
                            member=invoice.member,
                            received_by=payment_method,
                            sale=sale_obj,
                            discounted_amount=invoice.discount,
                            discount_name=invoice.promo_code
                        )
                        due_obj = Due.objects.create(
                            original_amount=invoice.total_amount,
                            due_amount=invoice_due,
                            paid_amount=payment_amount,
                            due_date=date.today(),
                            member=invoice.member,
                            invoice=invoice,
                            payment=payment_obj,
                            transaction=transaction_obj
                        )
                        MemberDue.objects.create(
                            amount_due=due_obj.due_amount,
                            due_date=date.today(),
                            amount_paid=due_obj.paid_amount,
                            payment_date=date.today(),
                            member=invoice.member,
                            due_reference=due_obj
                        )
                        log_activity_task.delay_on_commit(
                            request_data_activity_log(request),
                            verb="Creation",
                            severity_level="info",
                            description="User paid an invoice",
                        )
                        return Response(
                            {
                                "code": 200,
                                "status": "success",
                                "message": "Invoice payment successful",
                                "data": {
                                    "invoice_id": invoice.id
                                }
                            }, status=status.HTTP_200_OK
                        )
                    else:
                        payment_amount = 0
                        if adjust_from_balance:
                            member_account = MemberAccount.objects.get(
                                member=invoice.member)
                            member_account_balance = member_account.balance
                            if member_account_balance >= invoice.total_amount:
                                payment_amount = invoice.total_amount
                                member_account.balance = member_account_balance - invoice.total_amount
                                invoice.is_full_paid = True
                                invoice.status = "paid"
                                invoice.balance_due = 0
                            else:
                                payment_amount = member_account_balance
                                member_account.balance = 0
                                invoice.is_full_paid = False
                                invoice.balance_due = invoice.total_amount - payment_amount
                                if payment_amount != 0:
                                    invoice.status = "partial_paid"
                                else:
                                    invoice.status = "due"
                        member_account.save(update_fields=["balance"])
                        invoice.paid_amount = payment_amount
                        invoice_status = invoice.status
                        invoice_is_full_paid = invoice.is_full_paid
                        invoice.save(update_fields=[
                            "paid_amount", "is_full_paid", "status", "balance_due"])
                        if invoice_is_full_paid:
                            full_receiving_type, _ = IncomeReceivingType.objects.get_or_create(
                                name="full")
                        else:
                            full_receiving_type, _ = IncomeReceivingType.objects.get_or_create(
                                name="partial")

                        transaction_obj = Transaction.objects.create(
                            amount=payment_amount,
                            transaction_date=date.today(),
                            status=invoice_status,
                            member=invoice.member,
                            invoice=invoice,
                            payment_method=payment_method
                        )
                        payment_obj = Payment.objects.create(
                            payment_amount=payment_amount,
                            payment_status=invoice_status,
                            payment_date=date.today(),
                            invoice=invoice,
                            member=invoice.member,
                            payment_method=payment_method,
                            processed_by=request.user,
                            transaction=transaction_obj
                        )
                        sale_type, _ = SaleType.objects.get_or_create(
                            name=invoice.invoice_type.name)
                        sale_obj = Sale.objects.create(
                            sale_number=generate_unique_sale_number(),
                            sub_total=invoice.total_amount,
                            total_amount=invoice.paid_amount,
                            payment_status=invoice_status,
                            sale_source_type=sale_type,
                            customer=invoice.member,
                            payment_method=payment_method,
                            invoice=invoice,
                            due_date=date.today()
                        )
                        Income.objects.create(
                            receivable_amount=invoice.total_amount,
                            final_receivable=sale_obj.total_amount,
                            actual_received=invoice.paid_amount,
                            reaming_due=invoice.balance_due,
                            particular=income_particular,
                            received_from_type=received_from,
                            receiving_type=full_receiving_type,
                            member=invoice.member,
                            received_by=payment_method,
                            sale=sale_obj,
                            discounted_amount=invoice.discount,
                            discount_name=invoice.promo_code
                        )
                        due_obj = Due.objects.create(
                            original_amount=invoice.total_amount,
                            due_amount=invoice.balance_due,
                            paid_amount=invoice.paid_amount,
                            due_date=date.today(),
                            member=invoice.member,
                            invoice=invoice,
                            payment=payment_obj,
                            transaction=transaction_obj
                        )
                        MemberDue.objects.create(
                            amount_due=due_obj.due_amount,
                            due_date=date.today(),
                            amount_paid=due_obj.paid_amount,
                            payment_date=date.today(),
                            member=invoice.member,
                            due_reference=due_obj
                        )
                        log_activity_task.delay_on_commit(
                            request_data_activity_log(request),
                            verb="Creation",
                            severity_level="info",
                            description="User paid an invoice",
                        )
                        return Response(
                            {
                                "code": 200,
                                "status": "success",
                                "message": "Invoice payment successful",
                                "data": {
                                    "invoice_id": invoice.id
                                }
                            }, status=status.HTTP_200_OK
                        )

            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User tried to pay an invoice but faced an error",
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
                description="User tried to pay an invoice but faced an error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong.",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IncomeParticularView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = serializers.IncomeParticularSerializer(
                data=request.data)
            if serializer.is_valid():
                cache.delete("active_income_particulars")  # Invalidate cache
                serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User created an Income particular",
                )
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "New income particular created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User tried to create an Income particular but faced error",
                )
                return Response({
                    "code": 400,
                    "status": "success",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Creation",
                severity_level="info",
                description="User tried to create an Income particular but faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_errors": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            # implement caching
            data = cache.get("active_income_particulars")
            if not data:
                income_particular = IncomeParticular.objects.filter(
                    is_active=True)
                serializer = serializers.IncomeParticularSerializer(
                    income_particular, many=True)
                data = serializer.data
                cache.set("active_income_particulars", data, 60 * 30)

            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all income particulars",
            )
            return Response({
                "code": 200,
                "status": "success",
                "message": "list of all income particulars",
                "data": data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to create an Income particular but faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IncomeReceivedFromView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = serializers.IncomeReceivingOptionSerializer(
                data=request.data)
            if serializer.is_valid():
                # Invalidate cache
                cache.delete("active_income_receiving_options")
                serializer.save()
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User created and Income received from option",
                )
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "New income receiving option created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                log_activity_task.delay_on_commit(
                    request_data_activity_log(request),
                    verb="Creation",
                    severity_level="info",
                    description="User requested to create Income received from option and faced and error",
                )
                return Response({
                    "code": 400,
                    "status": "success",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Creation",
                severity_level="info",
                description="User requested to create Income received from option and faced and error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_errors": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            # implement caching
            data = cache.get("active_income_receiving_options")
            if not data:
                data = IncomeReceivingOption.objects.filter(is_active=True)
                serializer = serializers.IncomeReceivingOptionSerializer(
                    data, many=True)
                data = serializer.data
                cache.set("active_income_receiving_options", data, 60*30)

            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all income received from view list",
            )
            return Response({
                "code": 200,
                "status": "success",
                "message": "list of all income receiving option",
                "data": data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view all income received from but faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvoiceShowView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = Invoice.objects.select_related(
                "invoice_type", "generated_by", "member", "restaurant", "event"
            ).prefetch_related(
                Prefetch("invoice_items__restaurant_items"),
                Prefetch("invoice_items__products"),
                Prefetch("invoice_items__facility"),
                Prefetch("invoice_items__event_tickets"),
            ).order_by("id")

            # get query params
            is_full_paid = self.request.query_params.get("is_full_paid")
            invoice_type = self.request.query_params.get("invoice_type")
            member_id = self.request.query_params.get("member")
            status_name = self.request.query_params.get("status")

            # apply filters if query params are present
            if is_full_paid is not None:
                queryset = queryset.filter(
                    is_full_paid=is_full_paid.lower() == "true")

            if invoice_type is not None:
                queryset = queryset.filter(
                    invoice_type__name__iexact=invoice_type.lower())
            if member_id is not None:
                queryset = queryset.filter(member__member_ID=member_id)
            if status_name is not None:
                queryset = queryset.filter(status__iexact=status_name)

            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                queryset, request, view=self)
            serializer = serializers.InvoiceForViewSerializer(
                paginated_queryset, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all invoices",
            )
            return paginator.get_paginated_response({
                "code": 200,
                "status": "success",
                "message": "List of all invoices",
                "data": serializer.data
            }, status=200)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view all invoices but faced an error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvoiceSpecificView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            queryset = get_object_or_404(Invoice.objects.select_related(
                "invoice_type", "generated_by", "member", "restaurant", "event"
            ).prefetch_related(
                Prefetch("invoice_items__restaurant_items"),
                Prefetch("invoice_items__products"),
                Prefetch("invoice_items__facility"),
                Prefetch("invoice_items__event_tickets"),
            ), pk=id)
            serializer = serializers.InvoiceForViewSerializer(
                queryset)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed a single invoice",
            )
            return Response({
                "code": 200,
                "status": "success",
                "message": "Viewing a single invoice",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view a single invoice and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IncomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            query_items = sorted(request.query_params.items())
            query_string = urlencode(query_items) if query_items else "default"
            cache_key = f"income::{query_string}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data, status=200)

            # hit db if miss
            data = Income.objects.filter(is_active=True).select_related(
                "particular", "received_from_type", "receiving_type", "member", "received_by", "sale").order_by("id")
            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                data, request=request, view=self)
            serializer = serializers.IncomeSerializer(
                paginated_queryset, many=True)
            final_response = paginator.get_paginated_response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing the list of all income",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
            cache.set(cache_key, final_response.data, timeout=60*30)
            return final_response
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view a single invoice and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IncomeSpecificView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            queryset = Income.objects.select_related(
                "sale").filter(is_active=True).order_by("id")
            queryset = get_object_or_404(queryset, pk=id)
            serializer = serializers.IncomeSpecificSerializer(
                queryset)
            return Response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing the list of all income",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view a single invoice and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SalesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = Sale.objects.filter(is_active=True).order_by("id")
            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                data, request=request, view=self)
            serializer = serializers.SaleSerializer(
                paginated_queryset, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all sales",
            )
            return paginator.get_paginated_response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing the list of all sales",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view list of sales and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SalesSpecificView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            data = get_object_or_404(Sale, pk=id)
            serializer = serializers.SaleSpecificSerializer(
                data)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed a sale",
            )
            return Response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing the specific sale",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view a sale and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = Transaction.objects.filter(is_active=True).order_by("id")
            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                data, request=request, view=self)
            serializer = serializers.TransactionSerializer(
                paginated_queryset, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all transaction",
            )
            return paginator.get_paginated_response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing the list of all transaction",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view list of transaction and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionSpecificView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            data = get_object_or_404(Transaction, pk=id)
            serializer = serializers.TransactionSpecificSerializer(
                data)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed a transaction",
            )
            return Response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing the a specific transaction",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view a transaction and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = Payment.objects.filter(is_active=True).order_by("id")
            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                data, request=request, view=self)
            serializer = serializers.PaymentSerializer(
                paginated_queryset, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all payments",
            )
            return paginator.get_paginated_response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing the list of all payments",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view list of payments and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentSpecificView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            data = get_object_or_404(Payment, pk=id)
            serializer = serializers.PaymentSpecificSerializer(
                data)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed a payment",
            )
            return Response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing the a specific payment",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view a payment and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = Due.objects.filter(is_active=True).order_by("id")
            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                data, request=request, view=self)
            serializer = serializers.DuesSerializer(
                paginated_queryset, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all Dues",
            )
            return paginator.get_paginated_response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing the list of all dues",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view list of dues and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DueSpecificView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            data = get_object_or_404(Due, pk=id)
            serializer = serializers.DuesSpecificSerializer(
                data)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed a due",
            )
            return Response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing a specific due",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view a due and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberDueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = MemberDue.objects.filter(is_active=True).order_by("id")
            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                data, request=request, view=self)
            serializer = serializers.MemberDueSerializer(
                paginated_queryset, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all member dues",
            )
            return paginator.get_paginated_response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing the list of all member dues",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view list of member dues and faced error",
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
            serializer = serializers.MemberDuePaymentSerializer(
                data=request.data)
            if serializer.is_valid():
                member_due = serializer.validated_data["member_due_id"]
                payment_method = serializer.validated_data["payment_method"]
                amount = serializer.validated_data["amount"]
                adjust_from_balance = serializer.validated_data["adjust_from_balance"]
                due = member_due.due_reference
                invoice = due.invoice
                sale = Sale.objects.prefetch_related("income_sale").get(
                    invoice=invoice)
                income = sale.income_sale.first()
                due_amount = member_due.amount_due
                with transaction.atomic():

                    if amount == due_amount:
                        full_receiving_type, _ = IncomeReceivingType.objects.get_or_create(
                            name="full")
                        invoice.balance_due = 0
                        invoice.paid_amount += amount
                        invoice.is_full_paid = True
                        invoice.status = "paid"
                        invoice.save(update_fields=[
                                     "balance_due", "paid_amount", "is_full_paid", "status"])
                        transaction_obj = Transaction.objects.create(
                            amount=amount,
                            status="full_paid",
                            member=invoice.member,
                            invoice=invoice,
                            payment_method=payment_method
                        )
                        Payment.objects.create(
                            payment_amount=amount,
                            payment_status="paid",
                            invoice=invoice,
                            member=invoice.member,
                            payment_method=payment_method,
                            processed_by=request.user,
                            transaction=transaction_obj
                        )
                        # update Due table
                        due.due_amount = 0
                        due.paid_amount += amount
                        due.last_payment_date = date.today()
                        due.is_due_paid = True
                        due.transaction = transaction_obj
                        due.save(update_fields=[
                                 "due_amount", "paid_amount", "last_payment_date", "is_due_paid", "transaction"])

                        # update member due table
                        member_due.amount_due = 0
                        member_due.amount_paid += amount
                        member_due.payment_date = date.today()
                        member_due.is_due_paid = True
                        member_due.save(
                            update_fields=["amount_due", "amount_paid", "payment_date", "is_due_paid"])
                        # add data to income table
                        Income.objects.create(
                            receivable_amount=invoice.total_amount,
                            final_receivable=amount,
                            actual_received=amount,
                            reaming_due=0,
                            particular=income.particular,
                            received_from_type=income.received_from_type,
                            receiving_type=full_receiving_type,
                            member=invoice.member,
                            received_by=payment_method,
                            sale=sale
                        )
                        return Response({
                            "code": 200,
                            "status": "success",
                            "message": "Due paid successfully",
                            "data": {
                                "member_due": member_due.id
                            }
                        }, status=status.HTTP_200_OK)
                    else:

                        if adjust_from_balance:
                            member_account = MemberAccount.objects.get(
                                member=member_due.member)
                            member_account_balance = member_account.balance
                            if member_account_balance >= due_amount:
                                amount = due_amount
                                member_account.balance = member_account_balance - amount
                            else:
                                remaining_amount = due_amount-amount
                                if remaining_amount >= member_account_balance:
                                    amount += remaining_amount
                                    member_account.balance -= remaining_amount
                                else:
                                    amount += member_account_balance
                                    member_account.balance = 0
                            member_account.save(update_fields=["balance"])

                        if amount == due_amount:
                            full_receiving_type, _ = IncomeReceivingType.objects.get_or_create(
                                name="full")
                            invoice.balance_due = 0
                            invoice.paid_amount += amount
                            invoice.is_full_paid = True
                            invoice.status = "paid"
                            invoice.save(update_fields=[
                                "balance_due", "paid_amount", "is_full_paid", "status"])
                            transaction_obj = Transaction.objects.create(
                                amount=amount,
                                status="full_paid",
                                member=invoice.member,
                                invoice=invoice,
                                payment_method=payment_method
                            )
                            Payment.objects.create(
                                payment_amount=amount,
                                payment_status="paid",
                                invoice=invoice,
                                member=invoice.member,
                                payment_method=payment_method,
                                processed_by=request.user,
                                transaction=transaction_obj
                            )
                            # update Due table
                            due.due_amount = 0
                            due.paid_amount += amount
                            due.last_payment_date = date.today()
                            due.is_due_paid = True
                            due.transaction = transaction_obj
                            due.save(update_fields=[
                                "due_amount", "paid_amount", "last_payment_date", "is_due_paid", "transaction"])

                            # update member due table
                            member_due.amount_due = 0
                            member_due.amount_paid += amount
                            member_due.payment_date = date.today()
                            member_due.is_due_paid = True
                            member_due.save(
                                update_fields=["amount_due", "amount_paid", "payment_date", "is_due_paid"])
                            # add data to income table
                            Income.objects.create(
                                receivable_amount=invoice.total_amount,
                                final_receivable=amount,
                                actual_received=amount,
                                reaming_due=0,
                                particular=income.particular,
                                received_from_type=income.received_from_type,
                                receiving_type=full_receiving_type,
                                member=invoice.member,
                                received_by=payment_method,
                                sale=sale
                            )
                        else:
                            partial_receiving_type, _ = IncomeReceivingType.objects.get_or_create(
                                name="partial")
                            invoice.balance_due -= amount
                            invoice.paid_amount += amount
                            invoice.is_full_paid = False
                            invoice.status = "due"
                            invoice.save(update_fields=[
                                "balance_due", "paid_amount", "is_full_paid", "status"])
                            transaction_obj = Transaction.objects.create(
                                amount=amount,
                                status="partial_paid",
                                member=invoice.member,
                                invoice=invoice,
                                payment_method=payment_method
                            )
                            Payment.objects.create(
                                payment_amount=amount,
                                payment_status="due",
                                invoice=invoice,
                                member=invoice.member,
                                payment_method=payment_method,
                                processed_by=request.user,
                                transaction=transaction_obj
                            )
                            # update Due table
                            due.due_amount -= amount
                            due.paid_amount += amount
                            due.last_payment_date = date.today()
                            due.is_due_paid = False
                            due.transaction = transaction_obj
                            due.save(update_fields=[
                                "due_amount", "paid_amount", "last_payment_date", "is_due_paid", "transaction"])

                            # update member due table
                            member_due.amount_due -= amount
                            member_due.amount_paid += amount
                            member_due.payment_date = date.today()
                            member_due.is_due_paid = False
                            member_due.save(
                                update_fields=["amount_due", "amount_paid", "payment_date", "is_due_paid"])
                            # add data to income table
                            Income.objects.create(
                                receivable_amount=invoice.total_amount,
                                final_receivable=amount,
                                actual_received=amount,
                                reaming_due=member_due.amount_due,
                                particular=income.particular,
                                received_from_type=income.received_from_type,
                                receiving_type=partial_receiving_type,
                                member=invoice.member,
                                received_by=payment_method,
                                sale=sale
                            )
                    return Response({
                        "code": 200,
                        "status": "success",
                        "message": "Due paid successfully",
                        "data": {
                            "member_due": member_due.id
                        }
                    }, status=status.HTTP_200_OK)
            else:
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
                verb="View",
                severity_level="info",
                description="User tried to view a member due and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberDueSpecificView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            data = get_object_or_404(MemberDue, pk=id)
            serializer = serializers.MemberDueSpecificSerializer(
                data)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed a member due",
            )
            return Response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing a specific member due",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view a member due and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = MemberAccount.objects.filter(is_active=True).order_by("id")
            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                data, request=request, view=self)
            serializer = serializers.MemberAccountSerializer(
                paginated_queryset, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed all member accounts",
            )
            return paginator.get_paginated_response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing the list of all member accounts",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view list of member accounts and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberAccountSpecificSpecificView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            data = get_object_or_404(MemberAccount, member__member_ID=id)
            serializer = serializers.MemberAccountSerializer(
                data)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User viewed a member account",
            )
            return Response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Viewing a specific member account",
                    "data": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to view a member account and faced error",
            )
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
