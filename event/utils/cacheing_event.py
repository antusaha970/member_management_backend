from django.core.cache import cache
import pdb
import logging
logger = logging.getLogger("myapp")
def delete_item_related_keys(items):
    try:
        keys = cache.keys(f"{items}_*") 
        if keys:
            cache.delete_many(keys)
        else:
            logger.info("No keys found to delete.")
    except Exception as e:
        logger.error(f"Error deleting keys: {e}")

def caching_event_key(key, page, page_size):
    """
    Generates a unique cache key for event-related data.
    Args:
        key (str): The base key for the cache.
        page (int): The current page number.
        page_size (int): The number of items per page.
    Returns:
        str: A unique cache key for events.
    """
    return f"{key}_page_{page}_size_{page_size}"