from core.models import Gender
from core.models import Gender, MembershipType, InstituteName, MembershipStatusChoice, MaritalStatusChoice
from rest_framework import serializers


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
        is_exist = Gender.objects.filter(name=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                {'gender': f"Not a valid gender"})
        return value

    def validate_membership_type(self, value):
        is_exist = MembershipType.objects.filter(name=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                {'membership_type': f'{value} does not a valid membership type'})
        return value

    def validate_institute_name(self, value):
        is_exist = InstituteName.objects.filter(name=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                {'institute_name': f'{value} no institute with this name exists'})
        return value

    def validate_membership_status(self, value):
        is_exist = MembershipStatusChoice.objects.filter(name=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                {'membership_status': f'{value} no membership_status with this name exists'})
        return value

    def validate_marital_status(self, value):
        is_exist = MaritalStatusChoice.objects.filter(name=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                {'marital_status': f'{value} no marital_status with this name exists'})
        return value

    # TODO: Blood group and nationality validation


class MembersFinancialBasicsSerializer(serializers.Serializer):
    membership_fee = serializers.DecimalField(required=False)
    payment_received = serializers.DecimalField(required=False)
    membership_fee_remaining = serializers.DecimalField(required=False)
    subscription_fee = serializers.DecimalField(required=False)
    dues_limit = serializers.DecimalField(required=False)
    initial_payment_doc = serializers.FileField(required=False)
