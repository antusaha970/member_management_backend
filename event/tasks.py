
from django.core.cache import cache
from celery import shared_task


@shared_task
def delete_events_cache():
    try:
        cache.delete_pattern("events::*")
        return "success"
    except Exception as e:
        return str(e)
    
@shared_task
def delete_event_venues_cache():
    try:
        cache.delete_pattern("event_venues::*")
        return "success"
    except Exception as e:
        return str(e)
