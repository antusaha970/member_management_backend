from django.db import transaction
from django.utils import timezone
from member.models import (Address, ContactNumber, Descendant, 
EmergencyContact, Member, MemberHistory,
Documents, Profession, CompanionInformation,MembersFinancialBasics, 
Email, Spouse, Certificate, SpecialDay,


)
from member.tasks import delete_members_cache, delete_member_model_dependencies
from ..utils.utility_functions import log_request

    
    
    
class MemberBulkDeleteActionService:
    def __init__(self, request, members):
        self.request = request
        self.members = members
        self.member_ids = [m.id for m in members]

    def hard_delete(self):
        related_models = [
            ContactNumber, Email, Address, Spouse, Descendant,
            Profession, EmergencyContact, CompanionInformation,
            Documents, Certificate, SpecialDay, MembersFinancialBasics,
            MemberHistory
        ]

        with transaction.atomic():
            # Bulk delete related models in one query per model
            for model in related_models:
                model.objects.filter(member__in=self.member_ids).delete()

            # Finally bulk delete members
            Member.objects.filter(id__in=self.member_ids).delete()

            log_request(
                self.request,
                "All deleted members are permanently deleted",
                "info",
                f"All deleted members are permanently deleted. IDs: {self.member_ids}"
            )
            delete_members_cache.delay()

        return {
            "code": 204,
            "status": "success",
            "message": "All members are permanently deleted",
            "data": {"obj_ids": self.member_ids}
        }


    
class MemberSingleDeleteActionService:
    def __init__(self, request, member):
        self.request = request
        self.member = member

    def hard_delete(self):
        related_models = [
            ContactNumber, Email, Address, Spouse, Descendant,
            Profession, EmergencyContact, CompanionInformation,
            Documents, Certificate, SpecialDay, MembersFinancialBasics,
            MemberHistory
        ]

        with transaction.atomic():
            # Bulk delete related models in one query per model
            for model in related_models:
                model.objects.filter(member=self.member).delete()

            # Finally bulk delete members
            Member.objects.filter(id=self.member.id).delete()

            log_request(
                self.request,
                "This member is  permanently deleted",
                "info",
                "This member is permanently deleted."
            )
            delete_members_cache.delay()

        return {
            "code": 204,
            "status": "success",
            "message": "members are permanently deleted",
        }
