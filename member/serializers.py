from core.models import Gender
from core.models import Gender, MembershipType, InstituteName, MembershipStatusChoice, MaritalStatusChoice, BLOOD_GROUPS, COUNTRY_CHOICES
from rest_framework import serializers
from .models import Member, MembersFinancialBasics
from club.models import Club
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
                f"Not a valid gender")
        return value

    def validate_membership_type(self, value):
        is_exist = MembershipType.objects.filter(name=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f'{value} does not a valid membership type')
        return value

    def validate_institute_name(self, value):
        is_exist = InstituteName.objects.filter(name=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f'{value} no institute with this name exists')
        return value

    def validate_membership_status(self, value):
        is_exist = MembershipStatusChoice.objects.filter(name=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f'{value} no membership_status with this name exists')
        return value

    def validate_marital_status(self, value):
        is_exist = MaritalStatusChoice.objects.filter(name=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f'{value} no marital_status with this name exists')
        return value

    def validate_blood_group(self, value):
        if value is not None:
            valid_blood_groups = [bg[0] for bg in BLOOD_GROUPS]
            if value not in valid_blood_groups:
                raise serializers.ValidationError(
                    f"{value} is not a valid blood group")
        return value

    def validate_nationality(self, value):
        if value is not None:
            valid_countries = [cnt[1] for cnt in COUNTRY_CHOICES]
            if value not in valid_countries:
                raise serializers.ValidationError(
                    f"{value} is not a valid country")
        return value

    def validate_member_ID(self, value):
        is_same_id_exist = Member.objects.filter(member_ID=value).exists()
        if is_same_id_exist:
            raise serializers.ValidationError(
                f'{value} id already exists')

        return value

    def create(self, validated_data):
        club_data = validated_data.pop('club')
        gender_data = validated_data.pop('gender')
        membership_type_data = validated_data.pop('membership_type')
        institute_name_data = validated_data.pop('institute_name')
        membership_status_data = validated_data.pop('membership_status')
        marital_status_data = validated_data.pop('marital_status')
        club = Club.objects.get(pk=club_data)
        gender = Gender.objects.get(name=gender_data)
        membership_type = MembershipType.objects.get(name=membership_type_data)
        institute_name = InstituteName.objects.get(name=institute_name_data)
        membership_status = MembershipStatusChoice.objects.get(
            name=membership_status_data)
        marital_status = MaritalStatusChoice.objects.get(
            name=marital_status_data)
        member = Member.objects.create(club=club, gender=gender, membership_type=membership_type, institute_name=institute_name,
                                       membership_status=membership_status, marital_status=marital_status, **validated_data)
        return member


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

    def create(self, validated_data):
        member_ID = validated_data.pop("member_ID")
        member = Member.objects.get(member_ID=member_ID)
        member_financial_basics = MembersFinancialBasics.objects.create(member=member,
                                                                        **validated_data)

        return member_financial_basics


class MemberIdSerializer(serializers.Serializer):
    membership_type = serializers.CharField()

    def validate_membership_type(self, value):
        is_type_exist = MembershipType.objects.filter(name=value).exists()

        if not is_type_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid membership type")
        return value
