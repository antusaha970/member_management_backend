import requests
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


def request_data_activity_log(request):
    client_ip = get_client_ip(request)
    # client_ip = "8.8.8.8"
    if request.user is not None:
        user_id = request.user.id
    else:
        user_id = None
    data = {
        "user_id": user_id,
        "method": request.method,
        "path": request.path,
        "ip": client_ip,
        "location": get_location(client_ip),
        "user_agent": request.META.get("HTTP_USER_AGENT", "Unknown"),
        "device": request.META.get("COMPUTERNAME", "Unknown Device"),
        "referrer_url": request.META.get("HTTP_REFERER", "None"),

    }
    return data
