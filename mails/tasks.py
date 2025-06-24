
from celery import shared_task
from django.core.cache import cache
@shared_task
def delete_email_list_cache():
    try:
        cache.delete_pattern("email_lists::*")
        return "success"
    except Exception as e:
        return str(e)