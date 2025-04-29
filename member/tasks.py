from celery import shared_task
from .models import Member
from django.db import transaction
from .models import ContactNumber, Email, Address, Spouse, Descendant, Profession, EmergencyContact, CompanionInformation, Documents, Certificate, SpecialDay
from django.core.cache import cache

@shared_task
def delete_member_model_dependencies(id):
    try:
        member = Member.objects.get(id=id)
        with transaction.atomic():
            ContactNumber.objects.filter(
                member=member, is_active=True).update(is_active=False, status=2)
            Email.objects.filter(
                member=member, is_active=True).update(is_active=False, status=2)
            Address.objects.filter(
                member=member, is_active=True).update(is_active=False, status=2)
            Spouse.objects.filter(
                member=member, is_active=True).update(is_active=False, status=2)
            Descendant.objects.filter(
                member=member, is_active=True).update(is_active=False, status=2)
            Profession.objects.filter(
                member=member, is_active=True).update(is_active=False, status=2)
            EmergencyContact.objects.filter(
                member=member, is_active=True).update(is_active=False, status=2)
            CompanionInformation.objects.filter(
                member=member, is_active=True).update(is_active=False, status=2)
            Documents.objects.filter(
                member=member, is_active=True).update(is_active=False, status=2)
            Certificate.objects.filter(
                member=member, is_active=True).update(is_active=False, status=2)
            SpecialDay.objects.filter(
                member=member, is_active=True).update(is_active=False, status=2)
            return {"status": "success"}

    except Exception as E:
        return {"error": str(E)}


@shared_task
def delete_members_cache():
    try:
        cache.delete_pattern("members_list::*")
        cache.delete_pattern("specific_member_list::*")
        cache.delete_pattern("all_member_history::*")
        cache.delete_pattern("specific_member_history::*")
        return "success"
    except Exception as e:
        return str(e)
