# invoices/services/invoice_payment.py

from datetime import date, datetime
from django.db import transaction
from ...models import (
    Transaction, Payment, Sale, Due, MemberDue, Income, IncomeReceivingType, MemberAccount, SaleType
)
from ...utils.functions import generate_unique_sale_number
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log
from datetime import date
from django.db import transaction
from ...models import (
    Transaction, Payment, Sale, Due, MemberDue, Income,
    IncomeReceivingType, MemberAccount, SaleType
)
from ...utils.functions import generate_unique_sale_number
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log


# ---------------- HELPER FUNCTIONS ---------------- #
# updated table 
# MemberAccount
# Transaction
# Payment
# Sale
# Due
# MemberDue
# Income
# IncomeReceivingType
# SaleType

def adjust_member_balance(invoice, payment_amount, adjust_from_balance):
    """Adjust member account balance if requested."""
    if not adjust_from_balance:
        return payment_amount

    member_account = MemberAccount.objects.get(member=invoice.member)
    member_account_balance = member_account.balance
    remaining_payment = invoice.total_amount - payment_amount

    if member_account_balance >= remaining_payment:
        payment_amount += remaining_payment
        member_account.balance -= remaining_payment
    else:
        payment_amount += member_account_balance
        member_account.balance = 0

    member_account.save(update_fields=["balance"])
    return payment_amount


def update_invoice_payment_status(invoice, payment_amount):
    """Update invoice fields based on payment."""
    invoice.paid_amount = payment_amount

    if invoice.paid_amount == invoice.total_amount:
        invoice.is_full_paid = True
        invoice.status = "paid"
        invoice.balance_due = 0
    elif invoice.paid_amount == 0:
        invoice.is_full_paid = False
        invoice.status = "due"
        invoice.balance_due = invoice.total_amount
    else:
        invoice.is_full_paid = False
        invoice.status = "partial_paid"
        invoice.balance_due = invoice.total_amount - invoice.paid_amount

    invoice.save(update_fields=["paid_amount", "is_full_paid", "status", "balance_due"])
    return invoice


def create_transaction_and_payment(invoice, payment_amount, payment_method, user):
    """Create Transaction and Payment records."""
    transaction_obj = Transaction.objects.create(
        amount=payment_amount,
        transaction_date=date.today(),
        status=invoice.status,
        member=invoice.member,
        invoice=invoice,
        payment_method=payment_method,
    )
    payment_obj = Payment.objects.create(
        payment_amount=payment_amount,
        payment_status=invoice.status,
        payment_date=date.today(),
        invoice=invoice,
        member=invoice.member,
        payment_method=payment_method,
        processed_by=user,
        transaction=transaction_obj,
    )
    return transaction_obj, payment_obj


def create_sale_and_income(invoice, payment_amount, payment_method, income_particular, received_from):
    """Create Sale and Income records."""
    sale_type, _ = SaleType.objects.get_or_create(name=invoice.invoice_type.name)
    sale_obj = Sale.objects.create(
        sale_number=generate_unique_sale_number(),
        sub_total=invoice.total_amount,
        total_amount=invoice.paid_amount,
        payment_status=invoice.status,
        sale_source_type=sale_type,
        customer=invoice.member,
        payment_method=payment_method,
        invoice=invoice,
        due_date=date.today(),
    )

    receiving_type, _ = IncomeReceivingType.objects.get_or_create(
        name="full" if invoice.is_full_paid else "partial"
    )

    Income.objects.create(
        receivable_amount=invoice.total_amount,
        final_receivable=sale_obj.total_amount,
        actual_received=payment_amount,
        reaming_due=invoice.balance_due,
        particular=income_particular,
        received_from_type=received_from,
        receiving_type=receiving_type,
        member=invoice.member,
        received_by=payment_method,
        sale=sale_obj,
        discounted_amount=invoice.discount,
        discount_name=invoice.promo_code,
    )

    return sale_obj


def create_dues_if_needed(invoice, payment_amount, payment_obj, transaction_obj):
    """Create Due and MemberDue if invoice is not fully paid."""
    if invoice.balance_due <= 0:
        return None

    due_obj = Due.objects.create(
        original_amount=invoice.total_amount,
        due_amount=invoice.balance_due,
        paid_amount=payment_amount,
        due_date=date.today(),
        member=invoice.member,
        invoice=invoice,
        payment=payment_obj,
        transaction=transaction_obj,
    )
    MemberDue.objects.create(
        amount_due=due_obj.due_amount,
        due_date=date.today(),
        amount_paid=due_obj.paid_amount,
        payment_date=date.today(),
        member=invoice.member,
        due_reference=due_obj,
    )
    return due_obj


# ---------------- MAIN SERVICE ---------------- #

def process_invoice_payment(invoice, payment_method, amount, income_particular, received_from, adjust_from_balance, user, request):
    try:
        with transaction.atomic():
            # Step 1: Adjust member balance if needed
            payment_amount = adjust_member_balance(invoice, amount, adjust_from_balance)

            # Step 2: Update invoice status
            invoice = update_invoice_payment_status(invoice, payment_amount)

            # Step 3: Transaction + Payment
            transaction_obj, payment_obj = create_transaction_and_payment(
                invoice, payment_amount, payment_method, user
            )

            # Step 4: Sale + Income
            create_sale_and_income(invoice, payment_amount, payment_method, income_particular, received_from)

            # Step 5: Dues
            create_dues_if_needed(invoice, payment_amount, payment_obj, transaction_obj)

            # Step 6: Log success
            log_activity_task.delay_on_commit(
                request_data_activity_log(request),
                verb="Creation",
                severity_level="info",
                description="User paid an invoice",
            )

            return {"status": "success", "invoice_id": invoice.id}

    except Exception as e:
        log_activity_task.delay_on_commit(
            request_data_activity_log(request),
            verb="Creation",
            severity_level="error",
            description=f"Error while paying invoice: {str(e)}",
        )
        return {"status": "error", "error": str(e)}
