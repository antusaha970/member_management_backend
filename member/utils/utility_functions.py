from django.db.models import Max
from member.models import Member
import pdb
import re
from activity_log.tasks import log_activity_task
from activity_log.utils.functions import request_data_activity_log

# def generate_member_id(membership_type):
#     # Get the last member ID in the same membership type category
#     last_member = Member.objects.filter(
#         membership_type__name=membership_type).aggregate(Max('member_ID'))
#     last_member_id = last_member['member_ID__max']
#     if last_member_id:
#         # Separate the prefix (alphabetic part) and the numeric part
#         prefix = ''.join(filter(str.isalpha, last_member_id))
#         numeric_part = ''.join(filter(str.isdigit, last_member_id))

#         # Increment the numeric part, preserving its original length with zero-padding
#         new_id_number = str(int(numeric_part) + 1).zfill(len(numeric_part))
#     else:
#         # No existing member ID found, start with the prefix and '0001'
#         prefix = membership_type
#         new_id_number = '0001'

#     # Combine prefix and incremented numeric part for the new member ID
#     member_ID = f"{prefix}{new_id_number}"
#     return member_ID

# def generate_member_id(membership_type):
#     # Fetch all existing member IDs for the given membership type (excluding None values)
#     existing_ids = Member.objects.filter(
#         membership_type__name=membership_type
#     ).exclude(member_ID__isnull=True).values_list('member_ID', flat=True)
#     # Extract numeric parts from the member IDs
#     numeric_parts = sorted(
#         int(re.sub(r'\D', '', member_id))
#         for member_id in existing_ids if member_id and re.search(r'\d+', member_id)
#     )

#     # If no IDs exist, return the first available ID
#     if not numeric_parts:
#         return {"missing_ids": [], "next_available": f"{membership_type}0001"}

#     # Iterate through sorted numeric_parts to find missing numbers.
#     missing_numbers = []
#     previous = numeric_parts[0]
#     # If the first ID isn't 1, then 1 up to (first ID - 1) are missing.
#     if previous > 1:
#         missing_numbers.extend(range(1, previous))

#     for num in numeric_parts[1:]:
#         if num > previous + 1:
#             # Add all numbers between previous+1 and num-1
#             missing_numbers.extend(range(previous + 1, num))
#         previous = num

#     # Determine the next available ID:
#     # If there are missing numbers, use the smallest missing.
#     # Otherwise, use the number after the last existing ID.
#     if missing_numbers:
#         next_available = missing_numbers[0]
#     else:
#         next_available = numeric_parts[-1] + 1

#     # Format the missing IDs and the next available ID with zero-padding.
#     missing_ids = [
#         f"{membership_type}{str(num).zfill(4)}" for num in missing_numbers]
#     next_available_id = f"{membership_type}{str(next_available).zfill(4)}"

#     return {"missing_ids": missing_ids, "next_available": next_available_id}

# ------------------------------------------------------------------
def generate_member_id(membership_type,institute_code):
    # Fetch all existing member IDs for the given membership type (excluding None values)
    existing_ids = Member.objects.filter(
        membership_type__name=membership_type
    ).exclude(member_ID__isnull=True).values_list('member_ID', flat=True)
    # Extract numeric parts from the member IDs
    numeric_parts = sorted(
        int(re.sub(r'\D', '', member_id))
        for member_id in existing_ids if member_id and re.search(r'\d+', member_id)
    )

    # If no IDs exist, return the first available ID
    if not numeric_parts:
        return {"missing_ids": [], "next_available": f"{membership_type}0001-{institute_code}"}

    # Iterate through sorted numeric_parts to find missing numbers.
    missing_numbers = []
    previous = numeric_parts[0]
    # If the first ID isn't 1, then 1 up to (first ID - 1) are missing.
    if previous > 1:
        missing_numbers.extend(range(1, previous))

    for num in numeric_parts[1:]:
        if num > previous + 1:
            # Add all numbers between previous+1 and num-1
            missing_numbers.extend(range(previous + 1, num))
        previous = num

    # Determine the next available ID:
    # If there are missing numbers, use the smallest missing.
    # Otherwise, use the number after the last existing ID.
    if missing_numbers:
        next_available = missing_numbers[0]
    else:
        next_available = numeric_parts[-1] + 1

    # Format the missing IDs and the next available ID with zero-padding.
    missing_ids = [
        f"{membership_type}{str(num).zfill(4)}-{institute_code}" for num in missing_numbers]
    next_available_id = f"{membership_type}{str(next_available).zfill(4)}-{institute_code}"

    return {"missing_ids": missing_ids, "next_available": next_available_id}








def log_request(request, verb, level, description):
    log_activity_task.delay_on_commit(
        request_data_activity_log(request),
        verb=verb,
        severity_level=level,
        description=description,
    )
