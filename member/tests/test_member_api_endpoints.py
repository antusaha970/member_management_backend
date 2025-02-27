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
from member.utils.factories import *
import pdb
from unittest.mock import patch

from member.utils.permission_classes import AddMemberPermission
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
    is_active = True
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

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
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

        self.assertEqual(1, 1)


class SpouseApiEndpointTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        faker = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=faker.user_name(), password=faker.password(length=8)
        )
        cls.membership_status = SpouseStatusChoiceFactory.create_batch(3)
        image = generate_test_image()
        member = MemberFactory()

        cls.member_spouse_create_request_body = {
            "member_ID": member.member_ID,
            "spouse_name": faker.first_name(),
            "contact_number": faker.numerify(text='###########'),
            "spouse_dob": faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
            "image": image,
            "current_status": cls.membership_status[0].pk,
        }

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_spouse_creation_api_with_valid_data(self):
        response = self.client.post(
            "/api/member/v1/members/spouse/", self.member_spouse_create_request_body, format='multipart'
        )
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['status'], "success")
        self.assertEqual(response_data['code'], 201)
        self.assertIn("spouse_id", response_data["data"])

    def test_spouse_creation_api_with_invalid_data(self):
        """
        Test for checking member contact numbers are adding perfectly with invalid data
        """
        # arrange
        data = self.member_spouse_create_request_body
        data.pop("spouse_name")
        response = self.client.post(
            "/api/member/v1/members/spouse/", data, format='multipart')
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['status'], "failed")
        self.assertEqual(response_data['errors']['spouse_name'], [
                         'This field is required.'])
        self.assertIn("spouse_name", response_data["errors"])


class DescendantApiEndpointTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        faker = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=faker.user_name(), password=faker.password(length=8)
        )
        cls.descendant_relation = DescendantRelationChoiceFactory.create_batch(
            3)
        image = generate_test_image()
        member = MemberFactory()

        cls.member_descendant_create_request_body = {
            "member_ID": member.member_ID,
            "name": faker.first_name(),
            "contact_number": faker.numerify(text='###########'),
            "descendant_dob": faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
            "image": image,
            "current_status": cls.descendant_relation[0].pk,
        }

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_descendant_creation_api_with_valid_data(self):
        response = self.client.post(
            "/api/member/v1/members/descendants/", self.member_descendant_create_request_body, format='multipart'
        )
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['status'], "success")
        self.assertEqual(response_data['code'], 201)
        self.assertIn("descendant_id", response_data["data"])

    def test_descendant_creation_api_with_invalid_data(self):
        """
        Test for checking member contact numbers are adding perfectly with invalid data
        """
        # arrange
        data = self.member_descendant_create_request_body
        data.pop("name")
        response = self.client.post(
            "/api/member/v1/members/descendants/", data, format='multipart')
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['status'], "failed")
        self.assertEqual(response_data['errors']['name'], [
                         'This field is required.'])
        self.assertIn("name", response_data["errors"])


class CompanionApiEndpointTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        faker = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=faker.user_name(), password=faker.password(length=8)
        )
        image = generate_test_image()
        member = MemberFactory()

        # Request data for testing companion creation
        cls.member_companion_create_request_body = {
            "member_ID": member.member_ID,
            "companion_name": faker.first_name(),
            "companion_contact_number": faker.numerify(text='###########'),
            "companion_dob": faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
            "companion_image": image,  # This will likely need to be a file upload
            "relation_with_member": faker.first_name_male(),
        }

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_companion_creation_api_with_valid_data(self):
        response = self.client.post(
            "/api/member/v1/members/companion/", self.member_companion_create_request_body, format='multipart'
        )
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['status'], "success")
        self.assertEqual(response_data['code'], 201)
        self.assertIn("companion_id", response_data["data"])

    def test_companion_creation_api_with_invalid_data(self):
        """
        Test for checking member contact numbers are adding perfectly with invalid data
        """
        # arrange
        data = self.member_companion_create_request_body
        data.pop("companion_name")
        response = self.client.post(
            "/api/member/v1/members/companion/", data, format='multipart')
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['status'], "failed")
        self.assertEqual(response_data['errors']['companion_name'], [
                         'This field is required.'])
        self.assertIn("companion_name", response_data["errors"])


class DocumentApiEndpointTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        faker = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=faker.user_name(), password=faker.password(length=8)
        )
        member = MemberFactory()
        cls.image = generate_test_image()
        document_type = DocumentTypeChoiceFactory.create_batch(3)
        cls.document_create_request_body = {
            "member_ID": member.member_ID,
            "document_document": cls.image,
            "document_type": document_type[0].pk,
            "document_number": faker.numerify(text='#########'),

        }

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_document_creation_api_with_valid_data(self):
        response = self.client.post(
            "/api/member/v1/members/documents/", self.document_create_request_body, format='multipart'
        )
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['status'], "success")
        self.assertEqual(response_data['code'], 201)
        self.assertIn("document_id", response_data["data"])

    def test_document_creation_api_with_invalid_data(self):
        """
        Test for checking member document are adding perfectly with invalid data
        """
        # arrange
        data = self.document_create_request_body
        data.pop("document_document")
        response = self.client.post(
            "/api/member/v1/members/documents/", data, format='multipart')
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['status'], "failed")
        self.assertEqual(response_data['errors']['document_document'], [
                         'No file was submitted.'])
        self.assertIn("document_document", response_data["errors"])


class CertificateApiEndpointTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        faker = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=faker.user_name(), password=faker.password(length=8)
        )
        member = MemberFactory()
        cls.image = generate_test_image()
        cls.certificate_create_request_body = {
            "member_ID": member.member_ID,
            "title": faker.first_name(),
            "certificate_document": cls.image,
            "certificate_number": faker.numerify(text='#########'),

        }

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_certificate_creation_api_with_valid_data(self):
        response = self.client.post(
            "/api/member/v1/members/certificate/", self.certificate_create_request_body, format='multipart'
        )
        response_data = response.json()
        # print(response_data)
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['status'], "success")
        self.assertEqual(response_data['code'], 201)
        self.assertIn("id", response_data["data"])
        self.assertIn("title", response_data["data"])

    def test_certificate_creation_api_with_invalid_data(self):
        """
        Test for checking member certificate are adding perfectly with invalid data
        """
        # arrange
        data = self.certificate_create_request_body
        data.pop("certificate_document")
        response = self.client.post(
            "/api/member/v1/members/certificate/", data, format='multipart')
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['status'], "failed")
        self.assertEqual(response_data['message'], "Invalid request")
        self.assertEqual(response_data['errors']['certificate_document'], [
                         'No file was submitted.'])
        self.assertIn("certificate_document", response_data["errors"])


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
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.address_type = AddressTypeChoiceFactory()
        cls.user = get_user_model().objects.create_superuser(
            username=fake.user_name(), password=fake.password(length=6))

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_member_address_add_with_valid_data(self):
        """
            Test for member address add with valid data
        """

        # arrange
        _data = {
            "member_ID": self.member.member_ID,
            "data": [
                {
                    "address": fake.address(),
                    "is_primary": False,
                    "address_type": self.address_type.id
                },
                {
                    "address_type": self.address_type.id,
                    "title": fake.name(),
                    "address": fake.address(),
                    "is_primary": False
                }
            ]
        }

        # act
        _response = self.client.post(
            "/api/member/v1/members/address/", _data, format="json")

        # assert
        self.assertEqual(_response.status_code, 201)
        _response = _response.json()
        self.assertEqual(_response['code'], 201)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)

    def test_member_address_add_with_invalid_data(self):
        """
            Test for member address add with invalid data. Like missing data
        """

        # arrange
        _data = {
            "member_ID": self.member.member_ID,
            "data": [
                {
                    "is_primary": False,
                    "address_type": self.address_type.id
                },
                {
                    "address_type": self.address_type.id,
                    "title": fake.name(),
                    "address": fake.address(),
                    "is_primary": False
                }
            ]
        }

        # act
        _response = self.client.post(
            "/api/member/v1/members/address/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)
        self.assertEqual(_response['status'], "failed")
        self.assertIn("errors", _response)


class TestMemberJobInformationAddAndUpdate(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.user = get_user_model().objects.create_superuser(
            username=fake.user_name(), password=fake.password(length=8))

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_job_information_add_with_valid_data(self):
        """
        Test job information add with valid data.
        """
        # arrange
        _data = {
            "member_ID": self.member.member_ID,
            "data": [
                {
                    "title": fake.job(),
                    "organization_name": fake.company(),
                    "location": fake.country()
                }
            ]
        }

        # act
        _response = self.client.post(
            "/api/member/v1/members/job/", _data, format="json")

        # assert
        self.assertEqual(_response.status_code, 201)
        _response = _response.json()
        self.assertEqual(_response['code'], 201)
        self.assertEqual(_response["status"], "success")
        self.assertIn("data", _response)

    def test_job_information_add_with_invalid_data(self):
        """
        Test job information add with invalid data. Like missing fields
        """
        # arrange
        _data = {
            "member_ID": self.member.member_ID,
            "data": [
                {
                    "organization_name": fake.company(),
                    "location": fake.country()
                }
            ]
        }

        # act
        _response = self.client.post(
            "/api/member/v1/members/job/", _data, format="json")

        # assert
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)
        self.assertEqual(_response["status"], "failed")
        self.assertIn("errors", _response)


class TestMemberEmergencyContactAddAndUpdate(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.user = get_user_model().objects.create_superuser(
            username=fake.user_name(), password=fake.password(length=8))

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_member_emergency_contact_add_with_valid_data(self):
        """
        Test member emergency contact add with valid data
        """
        # arrange
        _data = {
            "member_ID": self.member.member_ID,
            "data": [
                {
                    "contact_name": fake.name(),
                    "contact_number": fake.random_number(digits=8)
                },
                {
                    "contact_name":
                        fake.name(),
                    "contact_number": fake.random_number(digits=8)
                }
            ]
        }

        # act
        _response = self.client.post(
            "/api/member/v1/members/emergency_contact/", _data, format="json")

        # assert
        self.assertEqual(_response.status_code, 201)
        _response = _response.json()
        self.assertEqual(_response['code'], 201)
        self.assertEqual(_response["status"], "success")
        self.assertIn("data", _response)

    def test_member_emergency_contact_add_with_invalid_data(self):
        """
        Test member emergency contact add with invalid data. Like missing fields
        """
        # arrange
        _data = {
            "member_ID": self.member.member_ID,
            "data": [
                {
                    "contact_number": fake.random_number(digits=8)
                },
                {
                    "contact_name":
                        fake.name(),
                    "contact_number": fake.random_number(digits=8)
                }
            ]
        }

        # act
        _response = self.client.post(
            "/api/member/v1/members/emergency_contact/", _data, format="json")

        # assert
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)
        self.assertEqual(_response["status"], "failed")
        self.assertIn("errors", _response)


class TestMemberSpecialDayAddAndUpdate(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.user = get_user_model().objects.create_superuser(
            username=fake.user_name(), password=fake.password(length=8))

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_member_special_day_add_with_valid_data(self):
        """
        Test member special day add with valid data
        """
        # arrange
        _data = {
            "member_ID": self.member.member_ID,
            "data": [
                {
                    "title": fake.name(),
                    "date": fake.date_between(start_date="-10y", end_date="today").strftime("%Y-%m-%d")
                },
                {
                    "title": fake.name(),
                    "date": fake.date_between(start_date="-10y", end_date="today").strftime("%Y-%m-%d")
                },
            ]
        }

        # act
        _response = self.client.post(
            "/api/member/v1/members/special_day/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 201)
        _response = _response.json()
        self.assertEqual(_response['code'], 201)
        self.assertEqual(_response["status"], "success")
        self.assertIn("data", _response)

    def test_member_special_day_add_with_invalid_data(self):
        """
        Test member special day add with invalid data. Like missing fields
        """
        # arrange
        _data = {
            "member_ID": self.member.member_ID,
            "data": [
                {
                    "date": fake.date_between(start_date="-10y", end_date="today").strftime("%Y-%m-%d")
                },
                {
                    "title": fake.name(),
                    "date": fake.date_between(start_date="-10y", end_date="today").strftime("%Y-%m-%d")
                },
            ]
        }

        # act
        _response = self.client.post(
            "/api/member/v1/members/special_day/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)
        self.assertEqual(_response["status"], "failed")
        self.assertIn("errors", _response)
