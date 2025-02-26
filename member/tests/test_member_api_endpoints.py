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
from ..utils.factories import *
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

    def test_member_creation_api_with_valid_data(self):
        """
        Test member creation with valid data
        """
        # arrange
        self.client.force_authenticate(user=self.user)
        # act
        _response = self.client.post(
            "/api/member/v1/members/", self.member_create_request_body, format='multipart')
        _response = _response.json()

        self.assertEqual(_response['code'], 201)
        self.assertEqual(_response['status'], "success")

    def test_member_creation_api_with_invalid_data(self):
        """
        Test member creation with invalid data. Check if we can create member without providing the required fields
        """
        # arrange
        self.client.force_authenticate(user=self.user)
        # act
        _data = self.member_create_request_body
        _data.pop("member_ID")
        _data.pop("gender")
        _data.pop("profile_photo")
        # assert
        _response = self.client.post(
            "/api/member/v1/members/", _data, format='multipart')
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)
        self.assertEqual(_response['status'], "failed")
        _errors = _response['errors']
        self.assertIn("member_ID", _errors)
        self.assertIn("gender", _errors)
        self.assertIn("profile_photo", _errors)


class TestMemberContactNumberAddAndUpdateTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.contact_type = ContactTypeFactory()
        cls.fake = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=fake.user_name(), password=fake.password(length=8))

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_member_contact_number_add_endpoint_with_valid_data(self):
        """
        Test for checking member contact numbers are adding perfectly with valid data
        """
        # arrange
        member_ID = self.member.member_ID
        _data = {
            'member_ID': member_ID,
            "data": [
                {
                    "number": self.fake.random_number(digits=6),
                    "contact_type": self.contact_type.id,
                    "is_primary": False
                },
                {
                    "number": self.fake.random_number(digits=6),
                    "contact_type": self.contact_type.id,
                    "is_primary": True
                }
            ]
        }

        # act

        _response = self.client.post(
            "/api/member/v1/members/contact_numbers/", _data, format="json")

        # assert
        self.assertEqual(_response.status_code, 201)
        _response = _response.json()
        self.assertEqual(_response['code'], 201)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)

    def test_member_contact_number_add_endpoint_with_invalid_data(self):
        """
        Test for checking member contact numbers endpoint with invalid data. Like contact type and missing data
        """
        # arrange
        member_ID = self.member.member_ID
        _data = {
            'member_ID': member_ID,
            "data": [
                {
                    "number": self.fake.random_number(digits=6),
                    "contact_type": self.contact_type.id+1,
                    "is_primary": False
                },
                {
                    "contact_type": self.contact_type.id,
                    "is_primary": True
                }
            ]
        }

        # act

        _response = self.client.post(
            "/api/member/v1/members/contact_numbers/", _data, format="json")

        # assert
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)
        self.assertEqual(_response['status'], "failed")
        self.assertIn("errors", _response)


class TestMemberEmailAddressAddAndUpdate(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.email_type = EmailTypeChoiceFactory()
        cls.fake = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=fake.user_name(), password=fake.password(length=8))
        cls.member = MemberFactory()

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_member_email_address_add_with_valid_data(self):
        """
        Test for checking member email address add api with valid data
        """
        # arrange
        _data = {
            "member_ID": self.member.member_ID,
            "data": [
                {
                    "email": self.fake.email(),
                    "is_primary": False
                },
                {
                    "email_type": self.email_type.id,
                    "email": self.fake.email(),
                    "is_primary": False
                }
            ]
        }
        # act
        _response = self.client.post(
            "/api/member/v1/members/email_address/", _data, format="json")

        # assert
        self.assertEqual(_response.status_code, 201)
        _response = _response.json()
        self.assertEqual(_response['code'], 201)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)


class TestMemberAddressAddAndUpdate(APITestCase):
    pass
