from core.models import Gender
from core.models import Gender, MembershipType, InstituteName, MembershipStatusChoice, MaritalStatusChoice, BLOOD_GROUPS, COUNTRY_CHOICES, ContactTypeChoice, EmailTypeChoice, AddressTypeChoice, SpouseStatusChoice, DescendantRelationChoice, DocumentTypeChoice
from rest_framework import serializers
from .models import Member, MembersFinancialBasics, ContactNumber, Email, Address, Spouse, Descendant, Profession, EmergencyContact, CompanionInformation, Documents, MemberHistory, SpecialDay, Certificate
from club.models import Club
import pdb
from .utils.utility_functions import generate_member_id
from django.utils import timezone


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
            membership_type = self.instance.membership_type.name
            present_id = self.instance.member_ID
            if present_id == value:
                return value

            if Member.objects.filter(membership_type__name=membership_type, member_ID=value).exists():
                raise serializers.ValidationError(
                    f"This member_ID {value} already exists for membership type {membership_type}."
                )
            return value

        is_same_id_exist = Member.objects.filter(member_ID=value).exists()
        if is_same_id_exist:
            raise serializers.ValidationError(
                f'{value} id already exists')

        return value

    def validate(self, attrs):
        if self.instance:
            member_ID = attrs.get("member_ID")
            first_two_characters = member_ID[:2]
            membership_type = attrs.get("membership_type")
            if membership_type != first_two_characters:
                raise serializers.ValidationError(f"Invalid member_ID")

        return super().validate(attrs)

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
        member_ID = validated_data.get('member_ID', instance.member_ID)
        membership_type = validated_data.get(
            'membership_type', instance.membership_type)
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
        membership_type_obj = MembershipType.objects.get(name=membership_type)

        gender = Gender.objects.get(name=gender)
        institute_name = InstituteName.objects.get(name=institute_name)
        membership_status = MembershipStatusChoice.objects.get(
            name=membership_status)
        marital_status = MaritalStatusChoice.objects.get(
            name=marital_status)

        flag = False
        if instance.member_ID != member_ID:
            flag = True
        # update information
        instance.member_ID = member_ID
        instance.first_name = first_name
        instance.last_name = last_name
        instance.gender = gender
        instance.date_of_birth = date_of_birth
        instance.batch_number = batch_number
        instance.anniversary_date = anniversary_date
        instance.profile_photo = profile_photo
        instance.blood_group = blood_group
        instance.nationality = nationality
        instance.membership_type = membership_type_obj
        instance.marital_status = marital_status
        instance.institute_name = institute_name
        instance.membership_status = membership_status
        # save the instance
        instance.save()
        if flag:
            old_records = MemberHistory.objects.filter(member=instance)
            update_lst = []
            for record in old_records:
                record.end_date = timezone.now()
                update_lst.append(record)
            MemberHistory.objects.bulk_update(update_lst, ['end_date'])
            history = MemberHistory(
                start_date=timezone.now(),
                stored_member_id=member_ID,
                transferred=True,
                transferred_reason="updated",
                member=instance
            )
            # save member history instance
            history.save()

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


class ContactDetailSerializer(serializers.Serializer):
    contact_type = serializers.PrimaryKeyRelatedField(
        queryset=ContactTypeChoice.objects.all(), required=False)
    number = serializers.CharField(max_length=20)
    is_primary = serializers.BooleanField(required=False)
    id = serializers.IntegerField(required=False)


class MemberContactNumberSerializer(serializers.Serializer):
    member_ID = serializers.CharField(required=True)
    data = serializers.ListSerializer(
        child=ContactDetailSerializer(), required=True)

    def validate_member_ID(self, value):
        if self.instance:
            return value
        is_exist = Member.objects.filter(member_ID=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid member id")
        return value

    def validate_data(self, value):
        """Ensure only one item in data has is_primary=True"""
        primary_count = sum(
            1 for item in value if item.get("is_primary", False))

        if primary_count > 1:
            raise serializers.ValidationError(
                "Only one contact can be marked as primary.")
        return value

    def create(self, validated_data):
        member_ID = validated_data["member_ID"]
        data = validated_data["data"]
        member = Member.objects.get(member_ID=member_ID)
        created_instances = []
        for item in data:
            ins = ContactNumber.objects.create(**item, member=member)
            created_instances.append({
                "status": "created",
                "contact_number_id": ins.id
            })
        return created_instances

    def update(self, instance, validated_data):
        """
        instance: A Member instance whose contact_numbers will be updated.
        validated_data: Dictionary containing:
            - member_ID (string)
            - data: A list of contact details (each may include an "id" if updating an existing contact)
        """
        data_list = validated_data.get('data', [])
        results = []

        # Iterate over each item in the submitted data
        for item in data_list:
            contact_id = item.get('id', None)
            if contact_id:
                # Update an existing contact number for the given member.
                try:
                    contact_obj = instance.contact_numbers.get(id=contact_id)
                except ContactNumber.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Contact with id {contact_id} does not exist for this member."
                    )
                # Update fields if provided; if not, retain current value.
                contact_obj.contact_type = item.get(
                    'contact_type', contact_obj.contact_type)
                contact_obj.number = item.get('number', contact_obj.number)
                contact_obj.is_primary = item.get(
                    'is_primary', contact_obj.is_primary)
                contact_obj.save()
                results.append({
                    "status": "updated",
                    "contact_number_id": contact_obj.id
                })
            else:
                # Optionally create a new contact number if no id is provided.
                new_contact = ContactNumber.objects.create(
                    member=instance, **item)
                results.append({
                    "status": "created",
                    "contact_number_id": new_contact.id
                })

        return results


class EmailAddressSerializer(serializers.Serializer):
    email_type = serializers.PrimaryKeyRelatedField(
        queryset=EmailTypeChoice.objects.all(), required=False)
    email = serializers.EmailField()
    is_primary = serializers.BooleanField(required=False)
    id = serializers.IntegerField(required=False)


class MemberEmailAddressSerializer(serializers.Serializer):
    member_ID = serializers.CharField(required=True)
    data = serializers.ListSerializer(
        child=EmailAddressSerializer(), required=True)

    def validate_member_ID(self, value):
        if self.instance:
            return value
        is_exist = Member.objects.filter(member_ID=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid member id")
        return value

    def validate_data(self, value):
        """Ensure only one item in data has is_primary=True"""
        primary_count = sum(
            1 for item in value if item.get("is_primary", False))

        if primary_count > 1:
            raise serializers.ValidationError(
                "Only one contact can be marked as primary.")
        return value

    def create(self, validated_data):
        member_ID = validated_data["member_ID"]
        data = validated_data["data"]
        member = Member.objects.get(member_ID=member_ID)
        created_instances = []
        for item in data:
            ins = Email.objects.create(**item, member=member)
            created_instances.append({
                "status": "created",
                "email_address_id": ins.id
            })
        return created_instances

    def update(self, instance, validated_data):
        """
        instance: A Member instance whose contact_numbers will be updated.
        validated_data: Dictionary containing:
            - member_ID (string)
            - data: A list of emails (each may include an "id" if updating an existing contact)
        """
        data_list = validated_data.get('data', [])
        results = []

        # Iterate over each item in the submitted data
        for item in data_list:
            email_id = item.get('id', None)
            if email_id:
                # Update an existing email for the given member.
                try:
                    email_obj = instance.emails.get(id=email_id)
                except Email.DoesNotExist:
                    raise serializers.ValidationError(
                        f"email with id {email_id} does not exist for this member."
                    )
                # Update fields if provided; if not, retain current value.
                email_obj.email_type = item.get(
                    'email_type', email_obj.email_type)
                email_obj.email = item.get('email', email_obj.email)
                email_obj.is_primary = item.get(
                    'is_primary', email_obj.is_primary)
                email_obj.save()
                results.append({
                    "status": "updated",
                    "email_id": email_obj.id
                })
            else:
                # Optionally create a new email if no id is provided.
                new_email = Email.objects.create(
                    member=instance, **item)
                results.append({
                    "status": "created",
                    "email_id": new_email.id
                })

        return results


class AddressSerializer(serializers.Serializer):
    address_type = serializers.PrimaryKeyRelatedField(
        queryset=AddressTypeChoice.objects.all(), required=False)
    address = serializers.CharField()
    is_primary = serializers.BooleanField(required=False)
    title = serializers.CharField(max_length=100, required=False)
    id = serializers.CharField(required=False)


class MemberAddressSerializer(serializers.Serializer):
    member_ID = serializers.CharField(required=True)
    data = serializers.ListSerializer(
        child=AddressSerializer(), required=True)

    def validate_member_ID(self, value):
        if self.instance:
            return value
        is_exist = Member.objects.filter(member_ID=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid member id")
        return value

    def validate_data(self, value):
        """Ensure only one item in data has is_primary=True"""
        primary_count = sum(
            1 for item in value if item.get("is_primary", False))

        if primary_count > 1:
            raise serializers.ValidationError(
                "Only one contact can be marked as primary.")
        return value

    def create(self, validated_data):
        member_ID = validated_data["member_ID"]
        data = validated_data["data"]
        member = Member.objects.get(member_ID=member_ID)
        created_instances = []
        for item in data:
            ins = Address.objects.create(**item, member=member)
            created_instances.append({
                "status": "created",
                "address_id": ins.id
            })
        return created_instances

    def update(self, instance, validated_data):
        """
        instance: A Member instance whose address will be updated.
        validated_data: Dictionary containing:
            - member_ID (string)
            - data: A list of emails (each may include an "id" if updating an existing contact)
        """
        data_list = validated_data.get('data', [])
        results = []

        # Iterate over each item in the submitted data
        for item in data_list:
            address_id = item.get('id', None)
            if address_id:
                # Update an existing email for the given member.
                try:
                    address_obj = instance.addresses.get(id=address_id)
                except Address.DoesNotExist:
                    raise serializers.ValidationError(
                        f"address with id {address_id} does not exist for this member."
                    )
                # Update fields if provided; if not, retain current value.
                address_obj.address_type = item.get(
                    'address_type', address_obj.address_type)
                address_obj.address = item.get('address', address_obj.address)
                address_obj.title = item.get(
                    'title', address_obj.title)
                address_obj.is_primary = item.get(
                    'is_primary', address_obj.is_primary)
                address_obj.save()
                results.append({
                    "status": "updated",
                    "address_id": address_obj.id
                })
            else:
                # Optionally create a new address if no id is provided.
                address = Address.objects.create(
                    member=instance, **item)
                results.append({
                    "status": "created",
                    "address_id": address.id
                })

        return results


class MemberSpouseSerializer(serializers.Serializer):
    spouse_name = serializers.CharField(max_length=100)
    contact_number = serializers.CharField(max_length=20, required=False)
    spouse_dob = serializers.DateField(required=False)
    image = serializers.ImageField(required=False)
    current_status = serializers.PrimaryKeyRelatedField(
        queryset=SpouseStatusChoice.objects.all(), required=False)
    member_ID = serializers.CharField()
    id = serializers.IntegerField(required=False)

    def validate_member_ID(self, value):

        is_exist = Member.objects.filter(member_ID=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid member id")
        return value

    def create(self, validated_data):
        spouse_name = validated_data['spouse_name']
        contact_number = validated_data.get("contact_number", "")
        spouse_dob = validated_data.get("spouse_dob")
        image = validated_data.get("image")
        current_status = validated_data.get("current_status")
        member_ID = validated_data['member_ID']
        member = Member.objects.get(member_ID=member_ID)
        instance = Spouse.objects.create(spouse_name=spouse_name, spouse_contact_number=contact_number,
                                         spouse_dob=spouse_dob, image=image, current_status=current_status, member=member)
        return instance

    def update(self, instance, validated_data):
        id = validated_data.get("id")
        if id is not None:
            spouse_obj = instance
            spouse_obj.spouse_name = validated_data.get(
                'spouse_name', spouse_obj.spouse_name)
            spouse_obj.spouse_contact_number = validated_data.get(
                'contact_number', spouse_obj.spouse_contact_number)
            spouse_obj.spouse_dob = validated_data.get(
                'spouse_dob', spouse_obj.spouse_dob)
            spouse_obj.image = validated_data.get('image', spouse_obj.image)
            spouse_obj.current_status = validated_data.get(
                'current_status', spouse_obj.current_status)
            spouse_obj.save()
            return spouse_obj

        return instance


class MemberSpecialDayDataSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    date = serializers.DateField(required=False)
    id = serializers.IntegerField(required=False)


class MemberSpecialDaySerializer(serializers.Serializer):
    member_ID = serializers.CharField(max_length=200)
    data = serializers.ListSerializer(
        child=MemberSpecialDayDataSerializer(), required=True)

    def validate_member_ID(self, value):

        is_exist = Member.objects.filter(member_ID=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid member id")
        return value

    def create(self, validated_data):
        member_ID = validated_data['member_ID']
        data = validated_data['data']
        member = Member.objects.get(member_ID=member_ID)

        created_instances = []
        for item in data:
            instance = SpecialDay.objects.create(**item, member=member)
            created_instances.append({
                "status": "created",
                "special_day_id": instance.id
            })

        return created_instances

    def update(self, instance, validated_data):

        data_list = validated_data.get('data', [])
        results = []

        # Iterate over each item in the submitted data
        for item in data_list:
            special_day_id = item.get('id', None)
            if special_day_id:
                try:
                    special_day_obj = instance.special_days.get(
                        id=special_day_id)
                except SpecialDay.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Special day with id {special_day_id} does not exist for this member."
                    )
                special_day_obj.title = item.get(
                    'title', special_day_obj.title)
                special_day_obj.date = item.get('date', special_day_obj.date)
                special_day_obj.save()
                results.append({
                    "status": "updated",
                    "special_day_id": special_day_obj.id
                })
            else:
                # Optionally create a new contact number if no id is provided.
                new_special_day = SpecialDay.objects.create(
                    member=instance, **item)
                results.append({
                    "status": "created",
                    "special_day_id": new_special_day.id
                })

        return results

    # def update(self, instance, validated_data):
    #     data = validated_data['data']
    #     updated_instances = []

    #     for item in data:
    #         special_day_id = item.get('id')
    #         if special_day_id is not None:
    #             special_day_obj = instance
    #             special_day_obj.title = item.get('title', special_day_obj.title)
    #             special_day_obj.date = item.get('date', special_day_obj.date)
    #             special_day_obj.save()
    #             updated_instances.append({
    #                 "status": "updated",
    #                 "special_day_id": special_day_obj.id
    #             })
    #         else:
    #             member_ID = validated_data.get("member_ID")
    #             if Member.objects.filter(member_ID=member_ID).exists():
    #                 raise serializers.ValidationError(
    #                     "No member exists with this id")
    #             member = Member.objects.get(member_ID=member_ID)
    #             instance = SpecialDay.objects.create(**item, member=member)
    #             updated_instances.append({
    #                 "status": "created",
    #                 "special_day_id": instance.id
    #             })

    #     return updated_instances


class MemberCertificateSerializer(serializers.Serializer):
    member_ID = serializers.CharField(max_length=200)
    title = serializers.CharField(max_length=100)
    certificate_number = serializers.CharField(max_length=100, required=False)
    certificate_document = serializers.FileField()
    id = serializers.IntegerField(required=False)

    def validate_member_ID(self, value):

        is_exist = Member.objects.filter(member_ID=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid member id")
        return value

    def validate_certificate_number(self, value):
        if not value.isalnum():
            raise serializers.ValidationError(
                "Certificate number must contain only letters and numbers.")
        return value

    def create(self, validated_data):
        member_ID = validated_data.pop('member_ID')
        member = Member.objects.get(member_ID=member_ID)
        instance = Certificate.objects.create(member=member, **validated_data)
        return instance

    def update(self, instance, validated_data):
        id = validated_data.get("id")
        if id is not None:
            certificate_obj = instance
            certificate_obj.title = validated_data.get(
                "title", certificate_obj.title)
            certificate_obj.certificate_number = validated_data.get(
                "certificate_number", certificate_obj.certificate_number)
            certificate_obj.certificate_document = validated_data.get(
                "certificate_document", certificate_obj.certificate_document)
            certificate_obj.save()
        else:
            member_ID = validated_data.pop("member_ID")
            if Member.objects.filter(member_ID=member_ID).exists():
                raise serializers.ValidationError(
                    "No member exists with this id")
            member = Member.objects.get(member_ID=member_ID)
            instance = Certificate.objects.create(
                **validated_data, member=member)
        return instance


class MemberDescendantsSerializer(serializers.Serializer):
    member_ID = serializers.CharField()
    descendant_contact_number = serializers.CharField(
        max_length=20, required=False)
    dob = serializers.DateField(required=False)
    image = serializers.ImageField(required=False)
    relation_type = serializers.PrimaryKeyRelatedField(
        queryset=DescendantRelationChoice.objects.all(), required=False)
    name = serializers.CharField(max_length=100)
    id = serializers.IntegerField(required=False)

    def validate_member_ID(self, value):
        if self.instance:
            return value
        is_exist = Member.objects.filter(member_ID=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid member id")
        return value

    def create(self, validated_data):
        id = validated_data.get("id")
        if id is not None:
            validated_data.pop("id")
        member_ID = validated_data.pop("member_ID")
        member = Member.objects.get(member_ID=member_ID)
        instance = Descendant.objects.create(**validated_data, member=member)
        return instance

    def update(self, instance, validated_data):
        id = validated_data.get("id")
        if id is not None:
            descendant_obj = instance
            descendant_obj.descendant_contact_number = validated_data.get(
                "descendant_contact_number", descendant_obj.descendant_contact_number)
            descendant_obj.dob = validated_data.get(
                "dob", descendant_obj.dob)
            descendant_obj.image = validated_data.get(
                "image", descendant_obj.image)
            descendant_obj.relation_type = validated_data.get(
                "relation_type", descendant_obj.relation_type)
            descendant_obj.name = validated_data.get(
                "name", descendant_obj.name)
            descendant_obj.save()
        else:
            member_ID = validated_data.pop("member_ID")
            if Member.objects.filter(member_ID=member_ID).exists():
                raise serializers.ValidationError(
                    "No member exists with this id")
            member = Member.objects.get(member_ID=member_ID)
            instance = Descendant.objects.create(
                **validated_data, member=member)
        return instance


class MemberJobDataSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    organization_name = serializers.CharField(max_length=150, required=False)
    location = serializers.CharField(max_length=100)
    job_description = serializers.CharField(required=False)
    location = serializers.CharField(max_length=100, required=False)
    id = serializers.IntegerField(required=False)


class MemberJobSerializer(serializers.Serializer):
    member_ID = serializers.CharField(max_length=200)
    data = serializers.ListSerializer(
        child=MemberJobDataSerializer(), required=True)

    def validate_member_ID(self, value):
        if self.instance:
            return value
        is_exist = Member.objects.filter(member_ID=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid member id")
        return value

    def create(self, validated_data):
        member_ID = validated_data.pop('member_ID')
        data = validated_data.pop('data')
        member = Member.objects.get(member_ID=member_ID)
        created_instance = []
        for job_data in data:
            instance = Profession.objects.create(**job_data, member=member)
            created_instance.append({
                'status': 'created',
                'job_id': instance.id
            })
        return created_instance

    def update(self, instance, validated_data):
        """
        instance: A Member instance whose Job will be updated.
        validated_data: Dictionary containing:
            - member_ID (string)
            - data: A list of title (each may include an "id" if updating an existing job)
        """
        data_list = validated_data.get('data', [])
        results = []

        # Iterate over each item in the submitted data
        for item in data_list:
            job_id = item.get('id', None)
            if job_id:
                # Update an existing email for the given member.
                try:
                    job_obj = instance.professions.get(id=job_id)
                except Profession.DoesNotExist:
                    raise serializers.ValidationError(
                        f"job with id {job_id} does not exist for this member."
                    )
                # Update fields if provided; if not, retain current value.
                job_obj.title = item.get(
                    'title', job_obj.title)
                job_obj.organization_name = item.get(
                    'organization_name', job_obj.organization_name)
                job_obj.job_description = item.get(
                    'job_description', job_obj.job_description)
                job_obj.location = item.get(
                    'location', job_obj.location)
                job_obj.save()
                results.append({
                    "status": "updated",
                    "job_id": job_obj.id
                })
            else:
                # Optionally create a new address if no id is provided.
                job = Profession.objects.create(
                    member=instance, **item)
                results.append({
                    "status": "created",
                    "job_id": job.id
                })

        return results


class MemberEmergencyContactDataSerializer(serializers.Serializer):
    contact_name = serializers.CharField(max_length=100)
    contact_number = serializers.CharField(max_length=20)
    relation_with_member = serializers.CharField(max_length=50, required=False)
    id = serializers.IntegerField(required=False)


class MemberEmergencyContactSerializer(serializers.Serializer):
    member_ID = serializers.CharField()
    data = serializers.ListSerializer(
        child=MemberEmergencyContactDataSerializer(), required=True)

    def validate_member_ID(self, value):
        if self.instance:
            return value
        is_exist = Member.objects.filter(member_ID=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid member id")
        return value

    def create(self, validated_data):
        member_ID = validated_data.pop("member_ID")
        data = validated_data.pop("data")
        member = Member.objects.get(member_ID=member_ID)
        created_instance = []
        for emergency_contact_data in data:
            instance = EmergencyContact.objects.create(
                **emergency_contact_data, member=member)
            created_instance.append({
                'status': "created",
                'emergency_contact_id': instance.id
            })
        return created_instance

    def update(self, instance, validated_data):
        """
        instance: A Member instance whose Emergency contact will be updated.
        validated_data: Dictionary containing:
            - member_ID (string)
            - data: A list of contact (each may include an "id" if updating an existing job)
        """
        data_list = validated_data.get('data', [])
        results = []

        # Iterate over each item in the submitted data
        for item in data_list:
            emergency_contact_id = item.get('id', None)
            if emergency_contact_id:
                # Update an existing email for the given member.
                try:
                    emergency_contact_obj = instance.emergency_contacts.get(
                        id=emergency_contact_id)
                except EmergencyContact.DoesNotExist:
                    raise serializers.ValidationError(
                        f"emergency contact with id {emergency_contact_id} does not exist for this member."
                    )
                # Update fields if provided; if not, retain current value.
                emergency_contact_obj.contact_name = item.get(
                    'contact_name', emergency_contact_obj.contact_name)
                emergency_contact_obj.contact_number = item.get(
                    'contact_number', emergency_contact_obj.contact_number)
                emergency_contact_obj.relation_with_member = item.get(
                    'relation_with_member', emergency_contact_obj.relation_with_member)
                emergency_contact_obj.save()
                results.append({
                    "status": "updated",
                    "emergency_contact_id": emergency_contact_obj.id
                })
            else:
                # Optionally create a new address if no id is provided.
                emergency_contact = EmergencyContact.objects.create(
                    member=instance, **item)
                results.append({
                    "status": "created",
                    "emergency_contact_id": emergency_contact.id
                })

        return results


class MemberCompanionInformationSerializer(serializers.Serializer):
    member_ID = serializers.CharField(max_length=200)
    companion_name = serializers.CharField(max_length=100)
    companion_dob = serializers.DateField(required=False)
    companion_contact_number = serializers.CharField(
        max_length=20, required=False)
    companion_card_number = serializers.CharField(
        max_length=50, required=False)
    relation_with_member = serializers.CharField(
        max_length=100, required=False)
    companion_image = serializers.ImageField(required=False)
    id = serializers.IntegerField(required=False)

    def validate_member_ID(self, value):

        is_exist = Member.objects.filter(member_ID=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid member id")
        return value

    def create(self, validated_data):
        member_ID = validated_data.pop("member_ID")
        member = Member.objects.get(member_ID=member_ID)
        instance = CompanionInformation.objects.create(
            **validated_data, member=member)
        return instance

    def update(self, instance, validated_data):
        id = validated_data.get("id")
        if id is not None:
            companion_info = instance
            companion_info.companion_name = validated_data.get(
                "companion_name", companion_info.companion_name)
            companion_info.companion_image = validated_data.get(
                "companion_image", companion_info.companion_image)
            companion_info.companion_dob = validated_data.get(
                "companion_dob", companion_info.companion_dob)
            companion_info.companion_contact_number = validated_data.get(
                "companion_contact_number", companion_info.companion_contact_number)
            companion_info.companion_card_number = validated_data.get(
                "companion_card_number", companion_info.companion_card_number)
            companion_info.relation_with_member = validated_data.get(
                "relation_with_member", companion_info.relation_with_member)
            companion_info.save()
            return companion_info
        return instance


class MemberDocumentSerializer(serializers.Serializer):
    member_ID = serializers.CharField()
    document_document = serializers.FileField()
    document_type = serializers.PrimaryKeyRelatedField(
        queryset=DocumentTypeChoice.objects.all())
    document_number = serializers.CharField(max_length=50, required=False)
    id = serializers.IntegerField(required=False)

    def validate_member_ID(self, value):
        if self.instance:
            is_exist = Member.objects.filter(member_ID=value).exists()
            if is_exist:
                return value
            else:
                raise serializers.ValidationError("Member does not exist")
        is_exist = Member.objects.filter(member_ID=value).exists()
        if not is_exist:
            raise serializers.ValidationError(
                f"{value} is not a valid member id")
        return value

    def create(self, validated_data):
        member_ID = validated_data.pop("member_ID")
        member = Member.objects.get(member_ID=member_ID)
        instance = Documents.objects.create(
            **validated_data, member=member)
        return instance

    def update(self, instance, validated_data):
        id = validated_data.get("id")
        if id is not None:
            document_obj = instance
            document_obj.document_document = validated_data.get(
                "document_document", document_obj.document_document)
            document_obj.document_type = validated_data.get(
                "document_type", document_obj.document_type)
            document_obj.document_number = validated_data.get(
                "document_number", document_obj.document_number)
            document_obj.save()
        else:
            member_ID = validated_data.pop("member_ID")
            if Member.objects.filter(member_ID=member_ID).exists():
                raise serializers.ValidationError(
                    "No member exists with this id")
            member = Member.objects.get(member_ID=member_ID)
            instance = Documents.objects.create(
                **validated_data, member=member)
        return instance


class MemberHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberHistory
        fields = "__all__"


class MemberContactNumberViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactNumber
        exclude = ["member"]
        depth = 1


class MemberEmailAddressViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        exclude = ["member"]
        depth = 1


class MemberAddressViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ["member"]
        depth = 1


class MemberSpouseViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spouse
        exclude = ["member"]


class MemberDescendantsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descendant
        exclude = ["member"]
        depth = 1


class MemberEmergencyContactViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        exclude = ["member"]
        depth = 1


class MemberCompanionViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanionInformation
        exclude = ["member"]
        depth = 1


class MemberDocumentsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documents
        exclude = ["member"]
        depth = 1


class MemberJobViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        exclude = ["member"]
        depth = 1


class MemberCertificateViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        exclude = ["member"]
        depth = 1


class MemberSpecialDaysViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialDay
        exclude = ["member"]
        depth = 1
