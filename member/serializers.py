from core.models import Gender
from core.models import Gender, MembershipType, InstituteName, MembershipStatusChoice, MaritalStatusChoice, BLOOD_GROUPS, COUNTRY_CHOICES
from rest_framework import serializers
from .models import Member
import pdb


class MemberSerializer(serializers.Serializer):
    club = serializers.IntegerField()
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

    def validate_blood_group(self, value):
        if value is not None:
            valid_blood_groups = [bg[0] for bg in BLOOD_GROUPS]
            if value not in valid_blood_groups:
                raise serializers.ValidationError({
                    'blood_group': f"{value} is not a valid blood group"
                })
        return value

    def validate_nationality(self, value):
        if value is not None:
            valid_countries = [cnt[1] for cnt in COUNTRY_CHOICES]
            if value not in valid_countries:
                raise serializers.ValidationError({
                    'nationality': f"{value} is not a valid country"
                })
        return value

    def validate_member_ID(self, value):
        is_same_id_exist = Member.objects.filter(member_ID=value).exists()
        if is_same_id_exist:
            raise serializers.ValidationError(
                {'member_ID': f'{value} id already exists'})

        return value


class MembersFinancialBasicsSerializer(serializers.Serializer):
    membership_fee = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2)
    payment_received = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2)
    membership_fee_remaining = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2)
    subscription_fee = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2)
    dues_limit = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2)
    initial_payment_doc = serializers.FileField(
        required=False)


class MemberIdSerializer(serializers.Serializer):
    membership_type = serializers.CharField()

    def validate_membership_type(self, value):
        is_type_exist = MembershipType.objects.filter(name=value).exists()

        if not is_type_exist:
            raise serializers.ValidationError({
                'membership_type': f"{value} is not a valid membership type"
            })
        return value
