from django.db.models import Max
from member.models import Member
import pdb


def generate_member_id(membership_type):
    # Get the last member ID in the same membership type category
    last_member = Member.objects.filter(
        membership_type__name=membership_type).aggregate(Max('member_ID'))
    last_member_id = last_member['member_ID__max']
    if last_member_id:
        # Separate the prefix (alphabetic part) and the numeric part
        prefix = ''.join(filter(str.isalpha, last_member_id))
        numeric_part = ''.join(filter(str.isdigit, last_member_id))

        # Increment the numeric part, preserving its original length with zero-padding
        new_id_number = str(int(numeric_part) + 1).zfill(len(numeric_part))
    else:
        # No existing member ID found, start with the prefix and '0001'
        prefix = membership_type
        new_id_number = '0001'

    # Combine prefix and incremented numeric part for the new member ID
    member_ID = f"{prefix}{new_id_number}"
    return member_ID
