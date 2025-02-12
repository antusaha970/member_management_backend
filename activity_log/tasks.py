
from activity_log.utils.functions import get_client_ip, get_location
import requests
from celery import shared_task
from django.utils.timezone import now
from .models import ActivityLog
import pdb
from django.contrib.auth import get_user_model
import logging
logger = logging.getLogger("myapp")


@shared_task
def log_activity_task(data, verb, severity_level, description):
    """Celery task to log user activity asynchronously."""
    try:
        user_id = data.get("user_id")
        method = data.get("method")
        path = data.get("path")
        ip = data.get("ip")
        location = data.get("location")
        user_agent = data.get("user_agent")
        device = data.get("device")
        referrer_url = data.get("referrer_url")
        timestamp = now()
        user_instance = get_user_model().objects.get(id=user_id)
        activity_log = ActivityLog.objects.create(
            user=user_instance,
            ip_address=ip,
            location=location,
            user_agent=user_agent,
            request_method=method,
            referrer_url=referrer_url,
            device=device,
            path=path,
            verb=verb,
            severity_level=severity_level,
            description=description,
            timestamp=timestamp,
        )
        return {"status": "success", "activity_log_id": activity_log.id}
    except get_user_model().DoesNotExist:
        return {"status": "error", "error": "User does not exist"}
    except Exception as e:
        logger.exception(str(e))
        return {"status": "error", "error": str(e)}
