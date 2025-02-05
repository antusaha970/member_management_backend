from django.core.cache import cache
from django_redis import get_redis_connection


def clear_user_permissions_cache():
    """
    Match the pattern and delete the cache for user permissions
    """
    redis_conn = get_redis_connection("default")
    keys_to_delete = list(redis_conn.scan_iter(
        "*user_permissions_*"))  # Get all keys matching pattern
    if keys_to_delete:
        redis_conn.delete(*keys_to_delete)  # Delete all keys at once
        print(f"Deleted cache keys: {keys_to_delete}")  # All keys
    else:
        print("No user permission caches found to clear.")


def add_no_cache_header_in_response(response):
    # Add headers to prevent caching
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response
