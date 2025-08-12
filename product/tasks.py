
from celery import shared_task
from django.core.cache import cache

@shared_task
def delete_products_cache():
    try:
        cache.delete_pattern("products::*")
        return "success"
    except Exception as e:
        return str(e)
