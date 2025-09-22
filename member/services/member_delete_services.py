from django.db import transaction
from django.utils import timezone
from event.models import Event, EventFee
from member.tasks import delete_members_cache, delete_member_model_dependencies
from ..utils.utility_functions import log_request
from django.db import transaction
from member.models import (
    ContactNumber, Email, Address, Spouse, Descendant, Profession, EmergencyContact,
    CompanionInformation, Documents, Certificate, SpecialDay, MemberHistory, MembersFinancialBasics, Member
)
from member_financial_management.models import (
    MemberAccount, Income, Invoice, Payment, Transaction, MemberDue, Due, Sale, InvoiceItem
)
from event.models import EventTicket, Event
from promo_code_app.models import AppliedPromoCode

class MemberBulkDeleteActionService:
    def __init__(self, request, members):
        self.request = request
        self.members = members
        self.member_ids = [m.id for m in members]

    def _delete_financials(self, member):
        MembersFinancialBasics.objects.filter(member=member).delete()
        MemberAccount.objects.filter(member=member).delete()
        MemberDue.objects.filter(member=member).delete()
        Due.objects.filter(member=member).delete()
        Payment.objects.filter(member=member).delete()
        Transaction.objects.filter(member=member).delete()
        Income.objects.filter(member=member).delete()
        Sale.objects.filter(customer=member).delete()

    def _delete_personal_info(self, member):
        ContactNumber.objects.filter(member=member).delete()
        Email.objects.filter(member=member).delete()
        Address.objects.filter(member=member).delete()
        Spouse.objects.filter(member=member).delete()
        Descendant.objects.filter(member=member).delete()
        Profession.objects.filter(member=member).delete()
        EmergencyContact.objects.filter(member=member).delete()
        CompanionInformation.objects.filter(member=member).delete()
        Documents.objects.filter(member=member).delete()
        Certificate.objects.filter(member=member).delete()
        SpecialDay.objects.filter(member=member).delete()
        MemberHistory.objects.filter(member=member).delete()

    def _delete_events(self, member):
        Event.objects.filter(organizer=member).delete()

    def _delete_promo_codes(self, member):
        AppliedPromoCode.objects.filter(used_by=member).delete()

    def _delete_invoices(self, member):
        InvoiceItem.objects.filter(invoice__member=member).delete()
        invoices = Invoice.objects.filter(member=member)
        for invoice in invoices:
            invoice.delete()

    def _delete_single_member(self, member):
        """Helper method to delete a single member and its dependencies."""
        self._delete_financials(member)
        self._delete_personal_info(member)
        self._delete_events(member)
        self._delete_promo_codes(member)
        self._delete_invoices(member)
        member.delete()

    def hard_delete(self):
        try:
            with transaction.atomic():
                for member in self.members:
                    self._delete_single_member(member)

            return {
                "code": 204,
                "status": "success",
                "message": "All members permanently deleted",
                "data": {"obj_ids": self.member_ids}
            }

        except Exception as e:
            return {
                "code": 500,
                "status": "failed",
                "message": "Failed to delete members due to related constraints",
                "data": {"errors": [str(e)]}
            }



class MemberSingleDeleteActionService:
    def __init__(self, request, member):
        self.request = request
        self.member = member

    def _delete_financials(self):
        MembersFinancialBasics.objects.filter(member=self.member).delete()
        MemberAccount.objects.filter(member=self.member).delete()
        MemberDue.objects.filter(member=self.member).delete()
        Due.objects.filter(member=self.member).delete()
        Payment.objects.filter(member=self.member).delete()
        Transaction.objects.filter(member=self.member).delete()
        Income.objects.filter(member=self.member).delete()
        Sale.objects.filter(customer=self.member).delete()

    def _delete_personal_info(self):
        ContactNumber.objects.filter(member=self.member).delete()
        Email.objects.filter(member=self.member).delete()
        Address.objects.filter(member=self.member).delete()
        Spouse.objects.filter(member=self.member).delete()
        Descendant.objects.filter(member=self.member).delete()
        Profession.objects.filter(member=self.member).delete()
        EmergencyContact.objects.filter(member=self.member).delete()
        CompanionInformation.objects.filter(member=self.member).delete()
        Documents.objects.filter(member=self.member).delete()
        Certificate.objects.filter(member=self.member).delete()
        SpecialDay.objects.filter(member=self.member).delete()
        MemberHistory.objects.filter(member=self.member).delete()

    def _delete_events(self):
        Event.objects.filter(organizer=self.member).delete()

    def _delete_promo_codes(self):
        AppliedPromoCode.objects.filter(used_by=self.member).delete()

    def _delete_invoices(self):
        InvoiceItem.objects.filter(invoice__member=self.member).delete()
        invoices = Invoice.objects.filter(member=self.member)
        for invoice in invoices:
            invoice.delete()

    def hard_delete(self):
        try:
            with transaction.atomic():
                # all related models are deleted here
                self._delete_financials()
                self._delete_personal_info()
                self._delete_events()
                self._delete_promo_codes()
                self._delete_invoices()

                # Finally, delete the member
                self.member.delete()

                log_request(
                    self.request,
                    "This member is permanently deleted",
                    "info",
                    "This member is permanently deleted."
                )
                delete_members_cache.delay()

            return {
                "code": 204,
                "status": "success",
                "message": "Member permanently deleted",
                "data": {"obj_id": self.member.id}
            }

        except Exception as e:
            return {
                "code": 500,
                "status": "failed",
                "message": "Failed to delete member due to related constraints",
                "data": {"errors": [str(e)]}
            }