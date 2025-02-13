from django.core.cache import cache
from django_redis import get_redis_connection
import secrets
import string


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


def generate_random_token(length=20):
    """Generate a secure random token of given length"""
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(secrets.choice(characters) for _ in range(length))


def set_blocking_system(cache_key, failed_attempts, block_key):
    cache.set(cache_key, failed_attempts,
              timeout=1800)  # Store for 30 mins
    if int(failed_attempts) == 10:
        cache.set(block_key, 120,
                  timeout=120)
    elif int(failed_attempts) >= 11 and int(failed_attempts) <= 15:
        pass
    elif int(failed_attempts) == 16:
        cache.set(block_key, 300,
                  timeout=300)
    elif int(failed_attempts) >= 17 and int(failed_attempts) <= 19:
        pass
    else:
        cache.set(block_key, 600,
                  timeout=600)
