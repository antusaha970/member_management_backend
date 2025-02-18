from django.db.models import Max
from member.models import Member
import pdb
import re


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

#     # Extract numeric parts, filter out invalid entries, and convert to a sorted list of integers
#     numeric_parts = sorted(
#         [int(re.sub(r'\D', '', member_id))
#          for member_id in existing_ids if member_id and re.search(r'\d+', member_id)]
#     )

#     # Find the lowest missing number
#     lowest_available = 1
#     for num in numeric_parts:
#         if num == lowest_available:
#             lowest_available += 1  # Move to the next available number
#         else:
#             break  # Found a gap, break early

#     # Construct the new member ID
#     member_ID = f"{membership_type}{str(lowest_available).zfill(4)}"
#     return member_ID


# def generate_member_id(membership_type):
#     # Fetch all existing member IDs for the given membership type (excluding None values)
#     existing_ids = Member.objects.filter(
#         membership_type__name=membership_type
#     ).exclude(member_ID__isnull=True).values_list('member_ID', flat=True)

#     # Extract numeric parts, filter out invalid entries, and convert to a sorted list of integers
#     numeric_parts = sorted(
#         [int(re.sub(r'\D', '', member_id))
#          for member_id in existing_ids if member_id and re.search(r'\d+', member_id)]
#     )

#     # Find all missing numbers in the sequence
#     missing_ids = []
#     if numeric_parts:
#         min_id = numeric_parts[0]
#         max_id = numeric_parts[-1]

#         full_range = set(range(min_id, max_id + 1))
#         existing_set = set(numeric_parts)
#         missing_numbers = sorted(full_range - existing_set)

#         # Convert missing numbers to formatted member IDs
#         missing_ids = [
#             f"{membership_type}{str(num).zfill(4)}" for num in missing_numbers]

#         # Find the next available highest ID
#         highest_available = f"{membership_type}{str(max_id + 1).zfill(4)}"
#     else:
#         # If there are no existing IDs, start from 0001
#         missing_ids = []
#         highest_available = f"{membership_type}0001"

#     return {"missing_ids": missing_ids, "highest_available": highest_available}


# def generate_member_id(membership_type):
#     # Fetch all existing member IDs for the given membership type (excluding None values)
#     existing_ids = Member.objects.filter(
#         membership_type__name=membership_type
#     ).exclude(member_ID__isnull=True).values_list('member_ID', flat=True)

#     # Extract numeric parts, filter out invalid entries, and convert to a sorted list of integers
#     numeric_parts = sorted(
#         [int(re.sub(r'\D', '', member_id))
#          for member_id in existing_ids if member_id and re.search(r'\d+', member_id)]
#     )

#     # If there are no existing IDs, start with the first ID
#     if not numeric_parts:
#         return [], f"{membership_type}0001"

#     # Find missing IDs using binary search
#     missing_numbers = []
#     expected_number = numeric_parts[0]

#     for num in numeric_parts:
#         while expected_number < num:
#             missing_numbers.append(expected_number)
#             expected_number += 1
#         expected_number += 1  # Move to the next expected number

#     # Determine the next highest available ID
#     highest_available = numeric_parts[-1] + 1

#     # Format the missing IDs and the highest available ID
#     missing_ids = [
#         f"{membership_type}{str(num).zfill(4)}" for num in missing_numbers]
#     next_available_id = f"{membership_type}{str(highest_available).zfill(4)}"

#     return {"missing_ids": missing_ids, "highest_available": next_available_id}


def generate_member_id(membership_type):
    # Fetch all existing member IDs for the given membership type (excluding None values)
    existing_ids = Member.objects.filter(
        membership_type__name=membership_type
    ).exclude(member_ID__isnull=True).values_list('member_ID', flat=True)

    # Extract numeric parts, filter out invalid entries, and convert to a sorted list of integers
    numeric_parts = sorted(
        [int(re.sub(r'\D', '', member_id))
         for member_id in existing_ids if member_id and re.search(r'\d+', member_id)]
    )

    # If no IDs exist, return the first available ID
    if not numeric_parts:
        return {"missing_ids": [], "highest_available": f"{membership_type}0001"}

    # Find missing IDs
    missing_numbers = []
    expected_number = numeric_parts[0]

    for num in numeric_parts:
        while expected_number < num:
            missing_numbers.append(expected_number)
            expected_number += 1
        expected_number += 1  # Move to the next expected number

    # Determine the highest available ID (largest missing number)
    highest_available = missing_numbers[-1] if missing_numbers else numeric_parts[-1] + 1

    # Format the missing IDs and the highest available ID
    missing_ids = [
        f"{membership_type}{str(num).zfill(4)}" for num in missing_numbers]

    return {
        "missing_ids": missing_ids,
        "highest_available": f"{membership_type}{str(highest_available).zfill(4)}"
    }
