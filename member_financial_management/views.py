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
                            amount=amount,
                            transaction_date=date.today(),
                            status="paid",
                            member=invoice.member,
                            invoice=invoice,
                            payment_method=payment_method
                        )
                        Payment.objects.create(
                            payment_amount=amount,
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
                        invoice.paid_amount = amount
                        invoice.is_full_paid = False
                        invoice.status = "partial_paid"
                        invoice.balance_due = invoice.total_amount - amount
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
                                balance=amount,
                                total_credits=due_obj.due_amount,
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
                                balance=amount,
                                total_credits=due_obj.due_amount,
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

                return Response("ok")
            else:
                return Response({
                    "code": 400,
                    "status": "failed",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
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
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "New income particular created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "code": 400,
                    "status": "success",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
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
            return Response({
                "code": 200,
                "status": "success",
                "message": "list of all income particulars",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
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
                return Response({
                    "code": 201,
                    "status": "success",
                    "message": "New income receiving option created",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "code": 400,
                    "status": "success",
                    "message": "Bad request",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
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
            return Response({
                "code": 200,
                "status": "success",
                "message": "list of all income receiving option",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
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
            invoices = Invoice.objects.select_related(
                "invoice_type", "generated_by", "member", "restaurant", "event"
            ).prefetch_related(
                Prefetch("invoice_items__restaurant_items"),
                Prefetch("invoice_items__products"),
                Prefetch("invoice_items__facility"),
                Prefetch("invoice_items__event_tickets"),
            ).order_by("id")
            serializer = serializers.InvoiceForViewSerializer(
                invoices, many=True)
            return Response({
                "code": 200,
                "status": "success",
                "message": "List of all invoices",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": 500,
                "status": "failed",
                "message": "Something went wrong",
                "errors": {
                    "server_error": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
