from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
from django.db import transaction
from datetime import date
import pdb
from .models import PaymentMethod, Transaction, Payment
from . import serializers
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
                with transaction.atomic():
                    if amount >= invoice.total_amount:
                        invoice.paid_amount = invoice.total_amount
                        invoice.is_full_paid = True
                        invoice.status = "paid"
                        invoice.balance_due = 0
                        invoice.save(update_fields=[
                            "paid_amount", "is_full_paid", "status", "balance_due"])
                        transaction_obj = Transaction.objects.create(
                            amount=amount,
                            transaction_date=date.today(),
                            status="paid",
                            member=invoice.member,
                            invoice=invoice,
                            payment_method=payment_method
                        )
                        payment_obj = Payment.objects.create(
                            payment_amount=amount,
                            payment_status="paid",
                            payment_date=date.today(),
                            invoice=invoice,
                            member=invoice.member,
                            payment_method=payment_method,
                            processed_by=request.user,
                            transaction=transaction_obj
                        )

                    elif amount < invoice.total_amount and amount != 0:
                        pass
                    else:
                        pass

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
