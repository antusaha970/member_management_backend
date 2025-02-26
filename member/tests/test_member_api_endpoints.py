from rest_framework.test import APITestCase
from faker import Faker
from django.contrib.auth import get_user_model
import factory
import random
import string
from datetime import date
from ..models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
import pdb

# Create a dummy image using PIL

fake = Faker()


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
    is_active = factory.Faker('boolean')
    created_at = factory.LazyFunction(date.today)
    updated_at = factory.LazyFunction(date.today)


class TestMemberCreateAndUpdateEndpoints(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Creates test data once for the whole test class."""
        faker = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=faker.user_name(), password=faker.password(length=8))
        gender = GenderFactory.create_batch(2)
        member_ship_type = MembershipTypeFactory.create_batch(3)
        institute = InstituteNameFactory.create_batch(3)
        membership_status = MembershipStatusChoiceFactory.create_batch(
            3)
        marital_status = MaritalStatusChoiceFactory.create_batch(3)
        image = generate_test_image()
        cls.member_create_request_body = {
            "member_ID": f"{member_ship_type[0].name}0001",
            "first_name": faker.first_name(),
            "gender": gender[0].name,
            "date_of_birth": faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
            "profile_photo": image,
            "membership_type": member_ship_type[0].name,
            "institute_name": institute[0].name,
            "membership_status": membership_status[0].name,
            "marital_status": marital_status[0].name,
            "last_name": faker.last_name(),
            "batch_number": faker.random_digit(),
            "anniversary_date": faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
            "blood_group": "B+",
            "nationality": "Bangladesh",
        }

    def test_member_creation_api(self):
        # arrange
        self.client.force_authenticate(user=self.user)
        # act
        _response = self.client.post(
            "/api/member/v1/members/", self.member_create_request_body, format='multipart')
        _response = _response.json()

        self.assertEqual(_response['code'], 201)
        self.assertEqual(_response['status'], "success")

    def test_member_factory(self):
        member = MemberFactory()
        pdb.set_trace()
        self.assertEqual(1, 1)
