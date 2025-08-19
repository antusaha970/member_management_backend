from django.db import transaction
from datetime import datetime
from ...models import Invoice, Transaction, Payment, Sale, Income, Due, MemberDue,IncomeReceivingType
from member_financial_management.utils.functions import generate_unique_sale_number
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log


def get_invoice(invoice_id):
    try:
        invoice = Invoice.active_objects.filter(pk=invoice_id).first()
        if not invoice:
            return None, {
                "status": "failed",
                "code": 404,
                "message": "No invoice found with this id.",
                "errors": {"invoice": ["No invoice found with this id."]}
            }
        return invoice, None
    except Exception as e:
        return None, {"status": "error", "error": str(e)}


def determine_income_type(paid_amount, total_amount):
    full_type, _ = IncomeReceivingType.objects.get_or_create(name="full")
    partial_type, _ = IncomeReceivingType.objects.get_or_create(name="partial")
    return full_type if paid_amount == total_amount else partial_type


def update_invoice_record(invoice, paid_amount):
    try:
        invoice.paid_amount = paid_amount
        invoice.balance_due = invoice.total_amount - paid_amount
        if paid_amount <= 0:
            invoice.status = "unpaid"
        elif 0 < paid_amount < invoice.total_amount:
            invoice.status = "partial_paid"
        else:
            invoice.status = "paid"
        invoice.save(update_fields=["balance_due", "paid_amount", "total_amount", "status"])
        return invoice, invoice.balance_due
    except Exception as e:
        raise e


def create_transaction_payment(invoice, paid_amount, payment_method, user):
    try:
        Transaction.objects.filter(invoice=invoice).update(is_active=False)
        Payment.objects.filter(invoice=invoice).update(is_active=False)

        transaction_obj = Transaction.objects.create(
            amount=paid_amount,
            member=invoice.member,
            invoice=invoice,
            payment_method=payment_method,
            notes="Transaction after updating invoice."
        )

        payment_obj = Payment.objects.create(
            payment_amount=paid_amount,
            payment_status=invoice.status,
            notes="Payment after updating invoice.",
            transaction=transaction_obj,
            invoice=invoice,
            member=invoice.member,
            payment_method=payment_method,
            processed_by=user
        )
        return transaction_obj, payment_obj
    except Exception as e:
        raise e


def update_sale_and_income(invoice, paid_amount, payment_method):
    try:
        old_sale = Sale.active_objects.select_related("sale_source_type").filter(invoice=invoice).first()
        print(f"Old Sale: {old_sale}")
        Sale.objects.filter(invoice=invoice).update(is_active=False)
        sale_obj = Sale.objects.create(
            sale_number=generate_unique_sale_number(),
            sub_total=invoice.total_amount,
            total_amount=invoice.total_amount,
            payment_status=invoice.status,
            due_date=datetime.today(),
            notes="Sale after updating invoice.",
            sale_source_type=old_sale.sale_source_type if old_sale else None,
            customer=invoice.member,
            payment_method=payment_method,
            invoice=invoice
        )

        old_income = Income.objects.select_related("particular", "received_from_type").filter(sale=old_sale).first()
        Income.objects.filter(sale=old_sale).update(is_active=False)
        income_receiving_type = determine_income_type(paid_amount, invoice.total_amount)
        Income.objects.create(
            receivable_amount=invoice.total_amount,
            final_receivable=invoice.total_amount,
            actual_received=paid_amount,
            reaming_due=invoice.balance_due,
            particular=old_income.particular,
            received_from_type=old_income.received_from_type,
            member=invoice.member,
            received_by=payment_method,
            sale=sale_obj,
            receiving_type=income_receiving_type
        )
        return sale_obj
    except Exception as e:
        raise e


def update_dues(invoice, paid_amount, transaction_obj, payment_obj):
    try:
        Due.objects.filter(invoice=invoice).update(is_active=False)
        old_due_ref = Due.objects.filter(invoice=invoice).first()
        if old_due_ref:
            MemberDue.objects.filter(due_reference=old_due_ref).update(is_active=False)

        if invoice.balance_due > 0:
            due_obj = Due.objects.create(
                original_amount=invoice.total_amount,
                due_amount=invoice.balance_due,
                paid_amount=paid_amount,
                due_date=datetime.today(),
                payment_status=invoice.status,
                member=invoice.member,
                invoice=invoice,
                payment=payment_obj,
                transaction=transaction_obj
            )
            MemberDue.objects.create(
                amount_due=due_obj.due_amount,
                due_date=datetime.today(),
                amount_paid=paid_amount,
                payment_date=datetime.today(),
                notes="Due created after updating invoice.",
                member=invoice.member,
                due_reference=due_obj
            )
    except Exception as e:
        raise e


def update_invoice(invoice_id, validated_data, user, request):
    try:
        invoice, error = get_invoice(invoice_id)
        if error:
            return error

        paid_amount = validated_data["paid_amount"]
        payment_method = validated_data["payment_method"]
       

        with transaction.atomic():
            invoice, balance_due = update_invoice_record(invoice, paid_amount)
            transaction_obj, payment_obj = create_transaction_payment(invoice, paid_amount, payment_method, user)
            update_sale_and_income(invoice, paid_amount, payment_method)
            update_dues(invoice, paid_amount, transaction_obj, payment_obj)

            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Update",
                severity_level="info",
                description="User Updated an invoice.",
            )

            return {"status": "success", "invoice": invoice}

    except Exception as e:
        log_activity_task.delay_on_commit(
            request_data_activity_log(request),
            verb="Update",
            severity_level="error",
            description=f"User faced an error updating invoice: {str(e)}",
        )
        return {"status": "error", "error": str(e)}
