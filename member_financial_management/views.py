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
from . import serializers
from .utils.functions import generate_unique_sale_number
logger = logging.getLogger("myapp")


class PaymentMethodView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = PaymentMethod.objects.filter(is_active=True)
            serializer = serializers.PaymentMethodSerializer(data, many=True)
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
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(str(e))
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Creation",
                severity_level="info",
                description="User tried to view payment method but faced error.",
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
                    severity_level="info",
                    description="User tried to create a new payment method but faced error.",
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
                description="User tried to create a new payment method but faced error.",
            )
            return Response({
                "code": 500,
                "status": "success",
                "message": "Added a new payment options",
                "errors": {
                    "server_errors": [str(e)]
                }
            }, status=status.HTTP_501_NOT_IMPLEMENTED)


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
                with transaction.atomic():
                    if amount >= invoice.total_amount:
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
                            sale=sale_obj
                        )
                        is_member_account_exist = MemberAccount.objects.filter(
                            member=invoice.member).exists()
                        if is_member_account_exist:
                            member_account = MemberAccount.objects.get(
                                member=invoice.member)
                            member_account.balance = member_account.balance + \
                                (amount-invoice.paid_amount)
                            member_account.total_debits = member_account.total_debits + amount
                            member_account.save(
                                update_fields=["balance", "total_debits"])
                        else:
                            MemberAccount.objects.create(
                                balance=amount-invoice.paid_amount,
                                total_debits=amount,
                                member=invoice.member,
                                last_transaction_date=date.today()
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
                        # TODO: Make right calculation
                        invoice.paid_amount = amount + invoice.paid_amount
                        if invoice.paid_amount == invoice.total_amount:
                            invoice.is_full_paid = True
                        else:
                            invoice.is_full_paid = False

                        invoice.status = "partial_paid"
                        invoice.balance_due = invoice.total_amount - invoice.paid_amount
                        invoice.save(update_fields=[
                            "paid_amount", "is_full_paid", "status", "balance_due"])
                        full_receiving_type, _ = IncomeReceivingType.objects.get_or_create(
                            name="partial")
                        transaction_obj = Transaction.objects.create(
                            amount=amount,
                            transaction_date=date.today(),
                            status="partial_paid",
                            member=invoice.member,
                            invoice=invoice,
                            payment_method=payment_method
                        )
                        payment_obj = Payment.objects.create(
                            payment_amount=amount,
                            payment_status="partial_paid",
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
                            invoice=invoice,
                            due_date=date.today()
                        )
                        Income.objects.create(
                            receivable_amount=invoice.total_amount,
                            final_receivable=sale_obj.total_amount,
                            actual_received=amount,
                            reaming_due=invoice.total_amount-amount,
                            particular=income_particular,
                            received_from_type=received_from,
                            receiving_type=full_receiving_type,
                            member=invoice.member,
                            received_by=payment_method,
                            sale=sale_obj
                        )
                        due_obj = Due.objects.create(
                            original_amount=invoice.total_amount,
                            due_amount=invoice.total_amount-amount,
                            paid_amount=amount,
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
                        is_member_account_exist = MemberAccount.objects.filter(
                            member=invoice.member).exists()

                        if is_member_account_exist:
                            member_account = MemberAccount.objects.get(
                                member=invoice.member)
                            member_account.balance = member_account.balance + amount
                            member_account.total_credits = member_account.total_credits + due_obj.due_amount
                            member_account.total_debits = member_account.total_debits + amount
                            member_account.save(
                                update_fields=["balance", "total_credits", "total_debits"])
                        else:
                            MemberAccount.objects.create(
                                balance=0,
                                total_credits=due_obj.due_amount,
                                total_debits=amount,
                                member=invoice.member,
                                last_transaction_date=date.today()
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
                        invoice.paid_amount = amount
                        invoice.is_full_paid = False
                        invoice.status = "due"
                        invoice.balance_due = invoice.total_amount - amount
                        invoice.save(update_fields=[
                            "paid_amount", "is_full_paid", "status", "balance_due"])
                        full_receiving_type, _ = IncomeReceivingType.objects.get_or_create(
                            name="partial")
                        transaction_obj = Transaction.objects.create(
                            amount=amount,
                            transaction_date=date.today(),
                            status="due",
                            member=invoice.member,
                            invoice=invoice,
                            payment_method=payment_method
                        )
                        payment_obj = Payment.objects.create(
                            payment_amount=amount,
                            payment_status="due",
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
                            payment_status="due",
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
                            reaming_due=invoice.total_amount-amount,
                            particular=income_particular,
                            received_from_type=received_from,
                            receiving_type=full_receiving_type,
                            member=invoice.member,
                            received_by=payment_method,
                            sale=sale_obj
                        )
                        due_obj = Due.objects.create(
                            original_amount=invoice.total_amount,
                            due_amount=invoice.total_amount-amount,
                            paid_amount=amount,
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
                        is_member_account_exist = MemberAccount.objects.filter(
                            member=invoice.member).exists()

                        if is_member_account_exist:
                            member_account = MemberAccount.objects.get(
                                member=invoice.member)
                            member_account.balance = member_account.balance + amount
                            member_account.total_credits = member_account.total_credits + due_obj.due_amount
                            member_account.total_debits = member_account.total_debits + amount
                            member_account.save(
                                update_fields=["balance", "total_credits", "total_debits"])
                        else:
                            MemberAccount.objects.create(
                                balance=0,
                                total_credits=due_obj.due_amount,
                                total_debits=amount,
                                member=invoice.member,
                                last_transaction_date=date.today()
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
            data = IncomeParticular.objects.filter(is_active=True)
            serializer = serializers.IncomeParticularSerializer(
                data, many=True)
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="View",
                severity_level="info",
                description="User tried to create an Income particular but faced error",
            )
            return Response({
                "code": 200,
                "status": "success",
                "message": "list of all income particulars",
                "data": serializer.data
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
            data = IncomeReceivingOption.objects.filter(is_active=True)
            serializer = serializers.IncomeReceivingOptionSerializer(
                data, many=True)
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
                "data": serializer.data
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
            data = Income.objects.filter(is_active=True).order_by("id")
            paginator = CustomPageNumberPagination()
            paginated_queryset = paginator.paginate_queryset(
                data, request=request, view=self)
            serializer = serializers.IncomeSerializer(
                paginated_queryset, many=True)
            return paginator.get_paginated_response(
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
