import factory
from core.models import *
from faker import Faker
from ..models import *
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date
import uuid

fake = Faker()


class ContactTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactTypeChoice

    name = factory.LazyAttribute(lambda _: fake.name())


class EmailTypeChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailTypeChoice

    name = factory.LazyAttribute(lambda _: fake.name())


class AddressTypeChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AddressTypeChoice

    name = factory.LazyFunction(fake.unique.word)


class SpouseStatusChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpouseStatusChoice
    name = factory.LazyAttribute(lambda _: fake.unique.word())


class DescendantRelationChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DescendantRelationChoice
    name = factory.LazyAttribute(lambda _: fake.unique.word())


class DocumentTypeChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DocumentTypeChoice
    name = factory.LazyAttribute(lambda _: fake.unique.word())


def generate_test_image():
    image = Image.new('RGB', (100, 100), color='red')  # Create a red image
    image_io = BytesIO()
    image.save(image_io, format='JPEG')  # Save image to BytesIO
    return SimpleUploadedFile("test_image.jpg", image_io.getvalue(), content_type="image/jpeg")


class GenderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Gender

    name = factory.LazyFunction(fake.unique.word)


class MembershipTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MembershipType

    name = factory.LazyFunction(fake.unique.word)


class InstituteNameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InstituteName

    name = factory.Faker('company')


class MembershipStatusChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MembershipStatusChoice

    name = factory.LazyFunction(fake.unique.word)


class MaritalStatusChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaritalStatusChoice

    name = factory.LazyAttribute(lambda _: fake.name())


class MemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Member

    # Foreign key relation (created first)
    membership_type = factory.SubFactory(MembershipTypeFactory)

    member_ID = factory.LazyAttribute(
        lambda obj: f"{obj.membership_type.name}{fake.random_digit()}")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    date_of_birth = factory.Faker(
        'date_of_birth', minimum_age=18, maximum_age=60)
    batch_number = factory.LazyFunction(lambda: fake.random_digit())
    anniversary_date = factory.Faker(
        'date_this_century', before_today=True, after_today=False)

    # Generate a dummy image file
    profile_photo = factory.LazyFunction(lambda: generate_test_image())

    blood_group = factory.Iterator(['A+', 'B+', 'O+', 'AB-', 'UNKNOWN'])
    nationality = factory.Iterator(['Bangladesh', 'India'])

    # Foreign key relations
    gender = factory.SubFactory(GenderFactory)
    institute_name = factory.SubFactory(InstituteNameFactory)
    membership_status = factory.SubFactory(MembershipStatusChoiceFactory)
    marital_status = factory.SubFactory(MaritalStatusChoiceFactory)

    # Record keeping
    status = 0
    is_active = True
    created_at = factory.LazyFunction(date.today)
    updated_at = factory.LazyFunction(date.today)
    

class SpouseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Spouse

    spouse_name = factory.Faker("name")
    spouse_contact_number = factory.Faker("phone_number")
    spouse_dob = factory.Faker('date_of_birth', minimum_age=18, maximum_age=60)
    image = factory.LazyFunction(lambda: generate_test_image())
    # Foreign Key Relations
    member = factory.SubFactory(MemberFactory)
    current_status = factory.SubFactory(SpouseStatusChoiceFactory)


class DescendantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Descendant

    name = factory.Faker("name")
    dob = factory.Faker('date_of_birth', minimum_age=1, maximum_age=100)
    image = factory.LazyFunction(lambda: generate_test_image())
    descendant_contact_number = factory.Faker('phone_number')
    # Foreign Key Relations

    relation_type = factory.SubFactory(DescendantRelationChoiceFactory)
    member = factory.SubFactory(MemberFactory)


class CompanionInformationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompanionInformation

    companion_name = factory.Faker("name")
    companion_contact_number = factory.Faker("phone_number")
    companion_dob = factory.Faker(
        'date_of_birth', minimum_age=1, maximum_age=100)
    companion_image = factory.LazyFunction(lambda: generate_test_image())
    relation_with_member = factory.Faker("name")
    companion_card_number = factory.Faker("phone_number")
    # Foreign Key Relations
    member = factory.SubFactory(MemberFactory)


class DocumentsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Documents

    document_number = factory.LazyFunction(lambda: str(fake.random_number(digits=10)))

    document_document = factory.Faker("file_path", extension="pdf")
    # Foreign Key Relations
    member = factory.SubFactory(MemberFactory)
    document_type = factory.SubFactory(DocumentTypeChoiceFactory)


class CertificateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Certificate

    title = factory.Faker("catch_phrase")
    certificate_number = factory.LazyAttribute(lambda _: str(uuid.uuid4()))
    certificate_document = factory.Faker("file_path", extension="pdf")
    # Foreign Key Relations
    member = factory.SubFactory(MemberFactory)


class ContactNumberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactNumber

    number = fake.random_number(digits=12)
    is_primary = False
    # relation (shared)
    member = factory.LazyAttribute(lambda _: shared_member)
    contact_type = factory.LazyAttribute(lambda _: shared_contact_type)
    # record keeping
    status = 0
    is_active = True
    created_at = factory.LazyFunction(date.today)
    updated_at = factory.LazyFunction(date.today)
    
class ContactNumberFakeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactNumber

    number = fake.random_number(digits=12)
    is_primary = False
    # relation (shared)
    member = factory.LazyAttribute(lambda _: shared_member)
    contact_type = factory.LazyAttribute(lambda _: getattr(_, 'shared_contact_type', "default_value"))
    

    # record keeping
    status = 0
    is_active = True
    created_at = factory.LazyFunction(date.today)
    updated_at = factory.LazyFunction(date.today)

class EmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Email

    email = factory.LazyAttribute(lambda _: fake.email())
    is_primary = False
    # relation (shared)
    member = factory.LazyAttribute(lambda _: shared_member)
    email_type = factory.LazyAttribute(lambda _: shared_contact_type)
    # record keeping
    status = 0
    is_active = True
    created_at = factory.LazyFunction(date.today)
    updated_at = factory.LazyFunction(date.today)


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    member = factory.LazyAttribute(lambda _: shared_member)
    address_type = factory.LazyAttribute(lambda _: shared_contact_type)

    title = factory.Faker("name")
    address = factory.Faker("name")
    is_primary = False

    # record keeping
    status = 0
    is_active = True
    created_at = factory.LazyFunction(date.today)
    updated_at = factory.LazyFunction(date.today)


class EmergencyContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmergencyContact

    contact_name = factory.Faker("name")
    contact_number = factory.Faker("phone_number")
    relation_with_member = factory.Faker("last_name")

    # relation (shared)
    member = factory.LazyAttribute(lambda _: shared_member)
    # record keeping
    status = 0
    is_active = True
    created_at = factory.LazyFunction(date.today)
    updated_at = factory.LazyFunction(date.today)


class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profession
    title = factory.Faker("name")
    organization_name = factory.Faker("name")
    job_description = factory.Faker("name"
                                    )
    location = factory.Faker("name")
    # relation (shared)
    member = factory.LazyAttribute(lambda _: shared_member)
    # record keeping
    status = 0
    is_active = True
    created_at = factory.LazyFunction(date.today)
    updated_at = factory.LazyFunction(date.today)


class SpecialDayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpecialDay
    title = factory.Faker("name")
    # relation (shared)
    member = factory.LazyAttribute(lambda _: shared_member)
    # record keeping
    status = 0
    is_active = True
    created_at = factory.LazyFunction(date.today)
    updated_at = factory.LazyFunction(date.today)
