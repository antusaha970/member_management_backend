from django.db import models
from core.models import Gender, BLOOD_GROUPS, COUNTRY_CHOICES, MembershipType, InstituteName, MembershipStatusChoice, MaritalStatusChoice, STATUS_CHOICES
from club.models import Club


class Member(models.Model):
    member_ID = models.CharField(
        max_length=200, unique=True)  # mandatory field
    first_name = models.CharField(
        max_length=200, blank=True, default="")  # mandatory field
    last_name = models.CharField(
        max_length=200, blank=True, default="")  # optional field
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL,
                               related_name="member_gender", null=True, blank=True)  # mandatory field
    date_of_birth = models.DateField(null=True, blank=True)  # mandatory field
    batch_number = models.CharField(
        max_length=500, default="")  # optional field
    anniversary_date = models.DateField(
        null=True, blank=True)  # optional field
    profile_photo = models.ImageField(
        upload_to='profile_photos/')  # mandatory field
    # choice fields
    blood_group = models.CharField(
        max_length=100, choices=BLOOD_GROUPS, default='UNKNOWN')  # optional field
    nationality = models.CharField(
        max_length=100, choices=COUNTRY_CHOICES, default='XX')  # optional field

    # relations
    membership_type = models.ForeignKey(
        MembershipType, related_name='membership_type_choice', on_delete=models.RESTRICT)  # mandatory field
    institute_name = models.ForeignKey(
        InstituteName, related_name='institute_name_choice', on_delete=models.RESTRICT)  # mandatory field
    membership_status = models.ForeignKey(
        MembershipStatusChoice, related_name='membership_status_choice', on_delete=models.RESTRICT)  # mandatory field
    marital_status = models.ForeignKey(
        MaritalStatusChoice, related_name='marital_status_choice', on_delete=models.RESTRICT)  # mandatory field

    # Record keeping
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name


class MembersFinancialBasics(models.Model):
    # optional field
    membership_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    # optional field
    payment_received = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    # optional field
    membership_fee_remaining = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    # optional field
    subscription_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    # optional field
    dues_limit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    initial_payment_doc = models.FileField(
        upload_to='initial_payment_doc/', blank=True, null=True)  # optional field

    # relations
    member = models.ForeignKey(
        Member, related_name='members_financial_basics', on_delete=models.RESTRICT)
    # Record keeping
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.member.member_ID
