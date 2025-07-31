
# from activity_log.utils.functions import get_client_ip, get_location
import requests
from celery import shared_task
from django.utils.timezone import now
from .models import ActivityLog
import pdb
from django.contrib.auth import get_user_model
import json
from django_redis import get_redis_connection
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
import logging
logger = logging.getLogger("myapp")


def enqueue_activity_log(data):
    conn = get_redis_connection("default")
    conn.rpush("activity_log_queue", json.dumps(data))


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
        dict_data = {
            'user': user_id,
            'ip_address': ip,
            'location': location,
            'user_agent': user_agent,
            'request_method': method,
            'referrer_url': referrer_url,
            'device': device,
            'path': path,
            'verb': verb,
            'severity_level': severity_level,
            'description': description,
            'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        enqueue_activity_log(dict_data)
        return {"status": "success", "details": "Push in queue"}

    except Exception as e:
        logger.exception(str(e))
        return {"status": "error", "error": str(e)}


@shared_task
def flush_activity_logs():
    conn = get_redis_connection("default")
    logs = []

    while True:
        raw = conn.lpop("activity_log_queue")
        if raw is None:
            break
        logs.append(json.loads(raw))

    logs_to_create = []
    User = get_user_model()

    for log in logs:
        user = None
        if log.get("user"):
            try:
                user = User.objects.get(pk=log["user"])
            except User.DoesNotExist:
                pass

        timestamp = parse_datetime(log["timestamp"])
        if timestamp and is_naive(timestamp):
            timestamp = make_aware(timestamp)

        logs_to_create.append(ActivityLog(
            user=user,
            ip_address=log["ip_address"],
            location=log["location"],
            user_agent=log["user_agent"],
            request_method=log["request_method"],
            referrer_url=log["referrer_url"],
            device=log["device"],
            path=log["path"],
            verb=log["verb"],
            severity_level=log["severity_level"],
            description=log["description"],
            timestamp=timestamp
        ))

    if logs_to_create:
        for i in range(0, len(logs_to_create), 100):
            ActivityLog.objects.bulk_create(logs_to_create[i:i+100])
        return f"{len(logs_to_create)} logs flushed"
    return "No logs to flush"
