import factory
from core.models import *
from faker import Faker
from ..models import *
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date
fake = Faker()


class ContactTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactTypeChoice

    name = factory.LazyAttribute(lambda _: fake.name())


class EmailTypeChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailTypeChoice

    name = fake.name()


class AddressTypeChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AddressTypeChoice

    name = fake.name()


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

    name = factory.Faker('word')


class MembershipTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MembershipType

    name = factory.Faker('word')


class InstituteNameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InstituteName

    name = factory.Faker('company')


class MembershipStatusChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MembershipStatusChoice

    name = factory.Faker('word')


class MaritalStatusChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaritalStatusChoice

    name = factory.Faker('word')


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
    status = factory.Iterator([0, 1, 2])
    is_active = True
    created_at = factory.LazyFunction(date.today)
    updated_at = factory.LazyFunction(date.today)


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
