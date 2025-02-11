
import requests
from celery import shared_task
from django.utils.timezone import now
from .models import ActivityLog
import pdb
from django.contrib.auth import get_user_model
import logging
logger = logging.getLogger("myapp")



def get_client_ip(request):
    """Extract real IP address from headers."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")

def get_location(ip):
    """Fetch location details using an external API."""
    reserved_ips = [
        "127.0.0.1",  
        "10.0.0.0",   
        "172.16.0.0",  
        "192.168.0.0", 
    ]
    
    if any(ip.startswith(reserved) for reserved in reserved_ips):
        return {}
    
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        if data["status"] == "success":
            return {
                "country": data.get("country"),
                "countryCode": data.get("countryCode"),
                "region": data.get("regionName"),
                "regionCode": data.get("region"),
                "city": data.get("city"),
                "zip": data.get("zip"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "timezone": data.get("timezone"),
                "isp": data.get("isp"),
                "org": data.get("org"),
                "as": data.get("as"),
                "query": data.get("query"),
            }
        else:
            return f"Failed to fetch location: {data.get('message')}"
    except Exception as e:
        logger.exception(str(e))
        return f"Location fetch failed: {str(e)}"
    
 
@shared_task
def log_activity_task(data,verb,severity_level,description):
    print("request",data)
    """Celery task to log user activity asynchronously."""
    try:
        user_id=data.get("user_id")
        method=data.get("method")
        path=data.get("path")
        ip=data.get("ip")
        location=data.get("location")
        user_agent=data.get("user_agent")
        device =data.get("device")
        referrer_url=data.get("referrer_url")
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

        # print(activity_log.id)
        return {"status": "success","activity_log_id": activity_log.id}

    except get_user_model().DoesNotExist:
        return {"status": "error", "error": "User does not exist"}
    
    except Exception as e:
        logger.exception(str(e))
        return {"status": "error", "error": str(e)}

