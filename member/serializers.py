from core.models import Gender
from core.models import Gender, MembershipType, InstituteName, MembershipStatusChoice, MaritalStatusChoice, BLOOD_GROUPS, COUNTRY_CHOICES
from rest_framework import serializers
from .models import Member, MembersFinancialBasics
from club.models import Club
import pdb


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
        # check if updating and instance
        if self.instance:
            return value

        is_same_id_exist = Member.objects.filter(member_ID=value).exists()
        if is_same_id_exist:
            raise serializers.ValidationError(
                f'{value} id already exists')

        return value

    def create(self, validated_data):

        gender_data = validated_data.pop('gender')
        membership_type_data = validated_data.pop('membership_type')
        institute_name_data = validated_data.pop('institute_name')
        membership_status_data = validated_data.pop('membership_status')
        marital_status_data = validated_data.pop('marital_status')
        gender = Gender.objects.get(name=gender_data)
        membership_type = MembershipType.objects.get(name=membership_type_data)
        institute_name = InstituteName.objects.get(name=institute_name_data)
        membership_status = MembershipStatusChoice.objects.get(
            name=membership_status_data)
        marital_status = MaritalStatusChoice.objects.get(
            name=marital_status_data)
        member = Member.objects.create(gender=gender, membership_type=membership_type, institute_name=institute_name,
                                       membership_status=membership_status, marital_status=marital_status, **validated_data)
        return member

    def update(self, instance, validated_data):
        first_name = validated_data.get('first_name', instance.first_name)
        last_name = validated_data.get('last_name', instance.last_name)
        gender = validated_data.get('gender', instance.gender)
        date_of_birth = validated_data.get(
            'date_of_birth', instance.date_of_birth)
        batch_number = validated_data.get(
            'batch_number', instance.batch_number)
        anniversary_date = validated_data.get(
            'anniversary_date', instance.anniversary_date)
        profile_photo = validated_data.get(
            'profile_photo', instance.profile_photo)
        blood_group = validated_data.get('blood_group', instance.blood_group)
        nationality = validated_data.get('nationality', instance.nationality)
        institute_name = validated_data.get(
            'institute_name', instance.institute_name)
        membership_status = validated_data.get(
            'membership_status', instance.membership_status)
        marital_status = validated_data.get(
            'marital_status', instance.marital_status)

        # get dependencies
        gender = Gender.objects.get(name=gender)
        institute_name = InstituteName.objects.get(name=institute_name)
        membership_status = MembershipStatusChoice.objects.get(
            name=membership_status)
        marital_status = MaritalStatusChoice.objects.get(
            name=marital_status)

        # update information
        instance.first_name = first_name
        instance.last_name = last_name
        instance.gender = gender
        instance.date_of_birth = date_of_birth
        instance.batch_number = batch_number
        instance.anniversary_date = anniversary_date
        instance.profile_photo = profile_photo
        instance.blood_group = blood_group
        instance.nationality = nationality
        instance.marital_status = marital_status
        instance.institute_name = institute_name
        instance.membership_status = membership_status

        # save the instance
        instance.save()

        return instance


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

    def update(self, instance, validated_data):
        # get the data from instance or
        membership_fee = validated_data.get(
            'membership_fee', instance.membership_fee)
        payment_received = validated_data.get(
            'payment_received', instance.payment_received)
        membership_fee_remaining = validated_data.get(
            'membership_fee_remaining', instance.membership_fee_remaining)
        subscription_fee = validated_data.get(
            'subscription_fee', instance.subscription_fee)
        dues_limit = validated_data.get('dues_limit', instance.dues_limit)
        initial_payment_doc = validated_data.get(
            'initial_payment_doc', instance.initial_payment_doc)

        # update the instance
        instance.membership_fee = membership_fee
        instance.payment_received = payment_received
        instance.membership_fee_remaining = membership_fee_remaining
        instance.subscription_fee = subscription_fee
        instance.dues_limit = dues_limit
        instance.initial_payment_doc = initial_payment_doc
        instance.save()

        return instance


class MemberIdSerializer(serializers.Serializer):
    membership_type = serializers.CharField()

    def validate_membership_type(self, value):
        is_type_exist = MembershipType.objects.filter(name=value).exists()

        if not is_type_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid membership type")
        return value


class MemberSerializerForViewSingleMember(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"
        depth = 1


class MembersFinancialBasicsSerializerForViewSingleMember(serializers.ModelSerializer):
    class Meta:
        model = MembersFinancialBasics
        exclude = ['id', 'member', 'status', 'created_at', 'updated_at']
