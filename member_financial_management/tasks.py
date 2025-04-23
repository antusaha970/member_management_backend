from celery import shared_task
from django.core.cache import cache


@shared_task
def delete_all_financial_cache():
    try:
        cache.delete_pattern("income::*")
        cache.delete_pattern("specific_income::*")
        cache.delete_pattern("sales::*")
        cache.delete_pattern("specific_sale::*")
        cache.delete_pattern("transactions::*")
        cache.delete_pattern("specific_transactions::*")
        cache.delete_pattern("payments::*")
        cache.delete_pattern("specific_payments::*")
        cache.delete_pattern("dues::*")
        cache.delete_pattern("specific_dues::*")
        cache.delete_pattern("member_dues::*")
        cache.delete_pattern("specific_member_due::*")
        cache.delete_pattern("member_accounts::*")
        cache.delete_pattern("specific_member_account::*")
        cache.delete_pattern("invoices::*")
        return "success"
    except Exception as e:
        return str(e)


@shared_task
def delete_invoice_cache():
    try:
        cache.delete_pattern("invoices::*")
        return "success"
    except Exception as e:
        return str(e)


@shared_task
def delete_member_accounts_cache():
    try:
        cache.delete_pattern("member_accounts::*")
        return "success"
    except Exception as e:
        return str(e)
