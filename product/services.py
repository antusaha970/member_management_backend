from decimal import Decimal
from django.db import transaction
from django.utils.timezone import now
from member_financial_management.utils.functions import generate_unique_invoice_number
from .models import  ProductPrice
from promo_code_app.models import AppliedPromoCode
from member_financial_management.models import Invoice, InvoiceItem, InvoiceType
from .tasks import delete_products_cache



def calculate_total_price(member, product_items):
    total_price = Decimal("0.00")
    product_ids = []
    product_ids_list = [item["product"].id for item in product_items]

    membership_prices = {
        (pp.product_id, pp.membership_type_id): pp.price
        for pp in ProductPrice.objects.filter(
            product_id__in=product_ids_list,
            membership_type=member.membership_type
        )
    }

    for item in product_items:
        product = item["product"]
        quantity = item["quantity"]
        price = membership_prices.get((product.id, member.membership_type_id), product.price)
        total_price += price * quantity
        product_ids.extend([product.id] * quantity)

    return total_price, Decimal("0.00"), product_ids


def apply_discount(total_price, promo_code):
    discount = Decimal("0.00")
    if promo_code:
        if promo_code.percentage:
            discount = (promo_code.percentage / Decimal("100")) * total_price
        else:
            discount = min(promo_code.amount, total_price)
        total_price -= discount
    return total_price, discount


def create_invoice(member, total_price, discount, promo_code, user):
    invoice_type, _ = InvoiceType.objects.get_or_create(name="Product")
    return Invoice.objects.create(
        currency="BDT",
        invoice_number=generate_unique_invoice_number(),
        balance_due=total_price,
        paid_amount=0,
        issue_date=now().date(),
        total_amount=total_price,
        is_full_paid=False,
        status="unpaid",
        invoice_type=invoice_type,
        generated_by=user,
        member=member,
        promo_code=promo_code if promo_code else "",
        discount=discount
    )


def update_stock(product_items):
    for item in product_items:
        product = item["product"]
        product.quantity_in_stock -= item["quantity"]
        product.save(update_fields=["quantity_in_stock"])
    # Clear the product cache
    delete_products_cache.delay()


def create_invoice_items(invoice, product_ids):
    invoice_item = InvoiceItem.objects.create(invoice=invoice)
    invoice_item.products.set(product_ids)


def apply_promo_usage(promo_code, discount, member):
    promo_code.remaining_limit -= 1
    promo_code.save(update_fields=["remaining_limit"])
    AppliedPromoCode.objects.create(
        discounted_amount=discount, promo_code=promo_code, used_by=member
    )
