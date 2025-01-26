from rest_framework import serializers
from core.models import Gender
# from .models import *

class MemberSerializer(serializers.Serializer):
    member_ID = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False)
    gender = serializers.CharField()
    date_of_birth = serializers.DateField()
    batch_number = serializers.CharField(required=False)
    anniversary_date = serializers.DateField(required=False)
    profile_photo = serializers.ImageField()
    blood_group = serializers.CharField(required=False)
    nationality = serializers.CharField(required=False)
    membership_type = serializers.CharField()
    institute_name = serializers.CharField()
    membership_status = serializers.CharField()
    marital_status = serializers.CharField()

    def validate_gender(self, value):
        pass


class MembersFinancialBasicsSerializer(serializers.Serializer):
    membership_fee = serializers.DecimalField(required=False)
    payment_received = serializers.DecimalField(required=False)
    membership_fee_remaining = serializers.DecimalField(required=False)
    subscription_fee = serializers.DecimalField(required=False)
    dues_limit = serializers.DecimalField(required=False)
    initial_payment_doc = serializers.FileField(required=False)  

    