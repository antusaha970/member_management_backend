from django.db import transaction
from django.utils import timezone
from member.models import (Address, ContactNumber, Descendant, 
EmergencyContact, Member, MemberHistory,
Documents, Profession, CompanionInformation,MembersFinancialBasics, 
Email, Spouse, Certificate, SpecialDay,


)
from member.tasks import delete_members_cache, delete_member_model_dependencies
from ..utils.utility_functions import log_request

class MemberDeleteActionService:
    def __init__(self, request, member):
        self.request = request
        self.member = member
        self.member_ID = member.member_ID

    def hard_delete(self):
        with transaction.atomic():
           
            ContactNumber.objects.filter(
                member=self.member).delete()
            Email.objects.filter(
                member=self.member).delete()
            Address.objects.filter(
                member=self.member).delete()
            Spouse.objects.filter(
                member=self.member).delete()
            Descendant.objects.filter(
                member=self.member).delete()
            Profession.objects.filter(
                member=self.member).delete()
            EmergencyContact.objects.filter(
                member=self.member).delete()
            CompanionInformation.objects.filter(
                member=self.member).delete()
            Documents.objects.filter(
                member=self.member).delete()
            Certificate.objects.filter(
                member=self.member).delete()
            SpecialDay.objects.filter(
                member=self.member).delete()
            MembersFinancialBasics.objects.filter(
                member=self.member).delete()
            MemberHistory.objects.filter(
                member=self.member).delete()
            self.member.delete()
           
            log_request(self.request, "Member hard delete success", "info",
                        "User successfully hard deleted a member")
            delete_members_cache.delay()
        return {
            'status_code': 204,
            'message': "Member hard deleted",
            'member_ID': self.member_ID
        }

    def soft_delete(self):
        with transaction.atomic():
            MemberHistory.objects.update_or_create(
                member=self.member,
                defaults={
                    "end_date": timezone.now(),
                    "transferred": True,
                    "stored_member_id": self.member.member_ID,
                    "transferred_reason": "deleted"
                }
            )
            Member.objects.filter(member_ID=self.member.member_ID).update(
                member_ID=None,
                status=2,
                is_active=False
            )
            delete_member_model_dependencies.delay_on_commit(self.member.id)
            log_request(self.request, "Member soft delete success", "info",
                        "User successfully soft deleted a member")
            delete_members_cache.delay()
        return {
            'status_code': 204,
            'message': "Member deleted",
            'member_ID': self.member_ID
        }

    def restore(self, member_id):
        with transaction.atomic():
            MemberHistory.objects.update_or_create(
                member=self.member,
                defaults={
                    "end_date": None,
                    "transferred": False,
                    "transferred_reason": "",
                    "stored_member_id": ""
                }
            )
            Member.objects.filter(member_ID=self.member_ID).update(
                status=0,
                is_active=True,
                member_ID=member_id
            )
            log_request(self.request, "Member restore success", "info",
                        "User successfully restored a member")
            delete_members_cache.delay()
        return {
            'status_code': 200,
            'message': "Member restored",
            'member_ID': member_id
        }

    def validate_member_ID(self, member_ID):

        is_exist = Member.objects.filter(member_ID=member_ID).exists()
        return is_exist
    
class MemberBulkDeleteActionService:
    def __init__(self, request, members):
        self.request = request
        self.members = members
        self.member_ids = [m.member_ID for m in members]

    def hard_delete(self):
        with transaction.atomic():
            for member in self.members:
                member.delete()
                delete_member_model_dependencies.delay_on_commit(member.id)
            log_request(self.request, "Bulk hard delete success", "info",
                        f"User successfully hard deleted members: {self.member_ids}")
            delete_members_cache.delay()
        return {
            'status_code': 204,
            'message': "Members hard deleted",
            'member_IDs': self.member_ids
        }

    def restore(self):
        with transaction.atomic():
            for member in self.members:
                MemberHistory.objects.filter(member=member).update(
                    end_date=None,
                    transferred=False,
                    transferred_reason=""
                )
                Member.objects.filter(member_ID=member.member_ID).update(
                    status=0,
                    is_active=True,
                    member_ID=member.member_ID
                )
            log_request(self.request, "Bulk restore success", "info",
                        f"User successfully restored members: {self.member_ids}")
            delete_members_cache.delay()
        return {
            'status_code': 200,
            'message': "Members restored",
            'member_IDs': self.member_ids
        }

    def soft_delete(self):
        with transaction.atomic():
            for member in self.members:
                MemberHistory.objects.filter(member=member).update(
                    end_date=timezone.now(),
                    transferred=True,
                    transferred_reason="deleted"
                )
                Member.objects.filter(member_ID=member.member_ID).update(
                    member_ID=None,
                    status=2,
                    is_active=False
                )
            log_request(self.request, "Bulk soft delete success", "info",
                        f"User successfully soft deleted members: {self.member_ids}")
            delete_members_cache.delay()
        return {
            'status_code': 204,
            'message': "Members soft deleted",
            'member_IDs': self.member_ids
        }

