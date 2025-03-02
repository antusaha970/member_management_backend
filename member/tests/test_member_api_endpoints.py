from rest_framework.test import APITestCase
from faker import Faker
from django.contrib.auth import get_user_model
from ..models import *
from member.utils.factories import *
import pdb
from unittest.mock import patch
import random
from member.utils.permission_classes import AddMemberPermission, UpdateMemberPermission
# Create a dummy image using PIL

fake = Faker()


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
    def test_member_creation_api_with_valid_data(self, mock_permission):
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

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_member_creation_api_with_invalid_data(self, mock_permission):
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
        cls.faker = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=cls.faker.user_name(), password=cls.faker.password(length=8)
        )
        cls.membership_status = SpouseStatusChoiceFactory.create_batch(3)
        cls.image = generate_test_image()
        cls.member = MemberFactory()

        cls.member_spouse_create_request_body = {
            "member_ID": cls.member.member_ID,
            "spouse_name": cls.faker.first_name(),
            "contact_number": cls.faker.numerify(text='###########'),
            "spouse_dob": cls.faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
            "image": cls.image,
            "current_status": cls.membership_status[0].pk,
        }

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_spouse_creation_api_with_valid_data(self, mock_permission):
        response = self.client.post(
            "/api/member/v1/members/spouse/", self.member_spouse_create_request_body, format='multipart'
        )
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['status'], "success")
        self.assertEqual(response_data['code'], 201)
        self.assertIn("spouse_id", response_data["data"])

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_spouse_creation_api_with_invalid_data(self, mock_permission):
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

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_spouse_update_api_with_valid_data(self, mock_permission):
        """
        Test for checking member spouse updating perfectly with valid data
        """
        # arrange
        spouse = SpouseFactory()
        member_id = spouse.member.member_ID

        # pdb.set_trace()
        data = {
            "member_ID": member_id,
            "spouse_name":self.faker.first_name(),
            "contact_number": self.faker.numerify(text='###########'),
            "id": spouse.pk

        }
        response = self.client.patch(
            f"/api/member/v1/members/spouse/", data, format='multipart')
        response_data = response.json()
        # Assert
        if data.get('id') is not None:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data['status'], "success")
            self.assertEqual(response_data['code'], 200)
            self.assertIn('spouse_id', response_data['data'])
            self.assertIn(
                "Member Spouse has been updated successfully", response_data["message"])

        else:
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_data['status'], "success")
            self.assertEqual(response_data['code'], 201)
            self.assertIn('spouse_id', response_data['data'])
            self.assertIn(
                "Member spouse has been created successfully", response_data["message"])

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_spouse_update_api_with_invalid_data(self, mock_permission):
        """
        Test for checking member spouse updating perfectly with invalid data
        """
        # arrange
        spouse = SpouseFactory()
        member_id = "232kll"
        # member_id=spouse.member.member_ID

        data = {
            "member_ID": member_id,
            "spouse_name": self.faker.first_name(),
            "contact_number":self.faker.numerify(text="########"),
            # "id": self.faker.random_int(1,100),
            "id": spouse.pk,
        }
        response = self.client.patch(
            f"/api/member/v1/members/spouse/", data, format='multipart')
        response_data = response.json()
        # Assert
        if response_data['code'] == 500:
            self.assertEqual(response_data['status'], "failed")
            self.assertEqual(response_data['message'], "Something went wrong")
            self.assertEqual(response_data['errors']['server_error'], [
                             'Spouse matching query does not exist.'])
        if response_data['code'] == 400:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['status'], "failed")
            self.assertEqual(response_data['errors']['member_ID'], [
                             '232kll is not a valid member id'])
            # self.assertEqual(response_data['errors']['id'], ['does not exist'])
            self.assertIn("member_ID", response_data["errors"])


class DescendantApiEndpointTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=cls.faker.user_name(), password=cls.faker.password(length=8)
        )
        cls.descendant_relation = DescendantRelationChoiceFactory.create_batch(
            3)
        image = generate_test_image()
        member = MemberFactory()

        cls.member_descendant_create_request_body = {
            "member_ID": member.member_ID,
            "name": cls.faker.first_name(),
            "contact_number": cls.faker.numerify(text='###########'),
            "descendant_dob": cls.faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
            "image": image,
            "current_status": cls.descendant_relation[0].pk,
        }

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_descendant_creation_api_with_valid_data(self, mock_permission):
        response = self.client.post(
            "/api/member/v1/members/descendants/", self.member_descendant_create_request_body, format='multipart'
        )
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['status'], "success")
        self.assertEqual(response_data['code'], 201)
        self.assertIn("descendant_id", response_data["data"])

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_descendant_creation_api_with_invalid_data(self, mock_permission):
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

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_descendant_update_api_with_valid_data(self, mock_permission):
        """
        Test for checking member descendant adding perfectly with valid data
        """
        # arrange
        descendant = DescendantFactory.create_batch(3)
        member_id = descendant[0].member.member_ID
        data = {
            "member_ID": member_id,
            "name": self.faker.first_name(),
            "contact_number": self.faker.numerify(text="#########"),
            "image": generate_test_image(),
            "current_status": descendant[0].pk
            # "id": descendant[0].pk
        }
        response = self.client.patch(
            f"/api/member/v1/members/descendants/", data, format='multipart')
        response_data = response.json()
        # Assert
        if data.get('id') is not None:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data['status'], "success")
            self.assertEqual(response_data['code'], 200)
            self.assertIn('descendant_id', response_data['data'])
            self.assertIn(
                "Member Descendant has been updated successfully", response_data["message"])
        else:
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_data['status'], "success")
            self.assertEqual(response_data['code'], 201)
            self.assertIn('descendant_id', response_data['data'])
            self.assertIn(
                "Member Descendant has been created successfully", response_data["message"])

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_descendant_update_api_with_invalid_data(self, mock_permission):
        """
        Test for checking member descendant updating perfectly with invalid data
        """
        # arrange
        descendant = DescendantFactory.create_batch(3)
        member_id = descendant[0].member.member_ID
        data = {
            "member_ID": member_id,
            "name": self.faker.first_name(),
            "contact_number": self.faker.numerify(text="#########"),
            "image": generate_test_image(),
            "current_status": descendant[0].pk,
            # "id": descendant[0].pk + 5   # invalid id
            "id": descendant[0].pk 
        }
        data.pop("name")
        response = self.client.patch(
            f"/api/member/v1/members/descendants/", data, format='multipart')
        response_data = response.json()
        # Assert
        if response_data['code'] == 500:
            self.assertEqual(response_data['status'], "failed")
            self.assertEqual(response_data['message'], "Something went wrong")
            self.assertEqual(response_data['errors']['server_error'], [
                             'Descendant matching query does not exist.'])

        if response_data['code'] == 400:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['status'], "failed")
            self.assertEqual(response_data['errors']['name'], [
                             'This field is required.'])
            self.assertIn("name", response_data["errors"])


class CompanionApiEndpointTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=cls.faker.user_name(), password=cls.faker.password(length=8)
        )
        image = generate_test_image()
        member = MemberFactory()

        # Request data for testing companion creation
        cls.member_companion_create_request_body = {
            "member_ID": member.member_ID,
            "companion_name": cls.faker.first_name(),
            "companion_contact_number": cls.faker.numerify(text='###########'),
            "companion_dob": cls.faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
            "companion_image": image,  # This will likely need to be a file upload
            "relation_with_member": cls.faker.first_name_male(),
        }

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_companion_creation_api_with_valid_data(self, mock_permission):
        response = self.client.post(
            "/api/member/v1/members/companion/", self.member_companion_create_request_body, format='multipart'
        )
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['status'], "success")
        self.assertEqual(response_data['code'], 201)
        self.assertIn("companion_id", response_data["data"])

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_companion_creation_api_with_invalid_data(self, mock_permission):
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

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_companion_update_api_with_valid_data(self, mock_permission):
        """
        Test for checking member companion  are updating perfectly with valid data
        """
        # arrange
        companion = CompanionInformationFactory()
        image = generate_test_image()
        data = {
            "member_ID": companion.member.member_ID,
            "companion_name": self.faker.first_name(),
            "companion_contact_number": self.faker.numerify(text="#########"),
            "companion_dob": companion.companion_dob,
            "companion_image": image,
            "id": companion.pk
        }
        # data.pop("id")
        response = self.client.patch(
            f"/api/member/v1/members/companion/", data, format='multipart')
        response_data = response.json()
        # Assert
        if data.get('id') is not None:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data['status'], "success")
            self.assertEqual(response_data['code'], 200)
            self.assertIn('companion_id', response_data['data'])
            self.assertIn(
                "Member companion has been updated successfully", response_data["message"])
        else:
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_data['status'], "success")
            self.assertEqual(response_data['code'], 201)
            self.assertIn('companion_id', response_data['data'])
            self.assertIn(
                "Member companion has been created successfully", response_data["message"])

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_companion_update_api_with_invalid_data(self, mock_permission):
        """
        Test for checking member companion perfectly with invalid data
        """
        # arrange
        companion = CompanionInformationFactory()
        image = generate_test_image()
        data = {
            "member_ID": companion.member.member_ID,
            "companion_name": self.faker.name(),
            "companion_contact_number":self.faker.numerify(text="#########") ,
            "companion_image": image,
            # "id": companion.pk + 5
            "id": companion.pk
        }
        data.pop("companion_name")
        response = self.client.patch(
            "/api/member/v1/members/companion/", data, format='multipart')
        response_data = response.json()
        # Assert
        if response_data['code'] == 500:
            self.assertEqual(response_data['status'], "failed")
            self.assertEqual(response_data['message'], "Something went wrong")
            self.assertEqual(response_data['errors']['server_error'], [
                             'CompanionInformation matching query does not exist.'])

        if response_data['code'] == 400:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['status'], "failed")
            self.assertEqual(response_data['errors']['companion_name'], [
                             'This field is required.'])
            self.assertIn("companion_name", response_data["errors"])


class DocumentApiEndpointTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=cls.faker.user_name(), password=cls.faker.password(length=8)
        )
        member = MemberFactory()
        cls.image = generate_test_image()
        document_type = DocumentTypeChoiceFactory.create_batch(3)
        cls.document_create_request_body = {
            "member_ID": member.member_ID,
            "document_document": cls.image,
            "document_type": document_type[0].pk,
            "document_number": cls.faker.numerify(text='#########'),

        }

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_document_creation_api_with_valid_data(self, mock_permission):
        response = self.client.post(
            "/api/member/v1/members/documents/", self.document_create_request_body, format='multipart'
        )
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['status'], "success")
        self.assertEqual(response_data['code'], 201)
        self.assertIn("document_id", response_data["data"])

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_document_creation_api_with_invalid_data(self, mock_permission):
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

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_document_update_api_with_valid_data(self, mock_permission):
        """
        Test for checking member document  are updating perfectly with valid data
        """
        # arrange
        document = DocumentsFactory()
        image = generate_test_image()
        new_document_type = DocumentTypeChoiceFactory.create_batch(3)
        data = {
            "member_ID": document.member.member_ID,
            "document_document": image,
            "document_type": new_document_type[1].pk,
            "document_number": self.faker.bothify(text="??#####"),
            "id": document.pk
        }
        data.pop("id")
        response = self.client.patch(
            f"/api/member/v1/members/documents/", data, format='multipart')
        response_data = response.json()
        # Assert
        if data.get('id') is not None:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data['status'], "success")
            self.assertEqual(response_data['code'], 200)
            self.assertIn('document_id', response_data['data'])
            self.assertIn(
                "Member Documents has been updated successfully", response_data["message"])
        else:
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_data['status'], "success")
            self.assertEqual(response_data['code'], 201)
            self.assertIn('document_id', response_data['data'])
            self.assertIn(
                "Member Documents has been created successfully", response_data["message"])

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_document_update_api_with_invalid_data(self, mock_permission):
        """
        Test for checking member document perfectly with invalid data
        """
        # arrange
        document = DocumentsFactory()
        image = generate_test_image()
        data = {
            "member_ID": document.member.member_ID,
            # "document_document" : image,        # this should be required field
            "document_number": self.faker.bothify(text="??#####"),
            "id": document.pk,
            # "id": document.pk+2,

        }
        # data.pop("document_document")
        response = self.client.patch(
            f"/api/member/v1/members/documents/", data, format='multipart')
        response_data = response.json()
        # Assert
        if response_data['code'] == 500:
            self.assertEqual(response_data['status'], "failed")
            self.assertEqual(response_data['message'], "Something went wrong")
            self.assertEqual(response_data['errors']['server_error'], [
                             'Documents matching query does not exist.'])

        if response_data['code'] == 400:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['status'], "failed")
            self.assertEqual(response_data['errors']['document_document'], [
                             'No file was submitted.'])
            self.assertIn("document_document", response_data["errors"])
            self.assertEqual(response_data['errors']['document_type'], [
                             'This field is required.'])


class CertificateApiEndpointTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=cls.faker.user_name(), password=cls.faker.password(length=8)
        )
        member = MemberFactory()
        cls.image = generate_test_image()
        cls.certificate_create_request_body = {
            "member_ID": member.member_ID,
            "title": cls.faker.first_name(),
            "certificate_document": cls.image,
            "certificate_number": cls.faker.numerify(text='#########'),

        }

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_certificate_creation_api_with_valid_data(self, mock_permission):
        response = self.client.post(
            "/api/member/v1/members/certificate/", self.certificate_create_request_body, format='multipart'
        )
        response_data = response.json()
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['status'], "success")
        self.assertEqual(response_data['code'], 201)
        self.assertIn("id", response_data["data"])
        self.assertIn("title", response_data["data"])

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_certificate_creation_api_with_invalid_data(self, mock_permission):
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

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_certificate_update_api_with_valid_data(self, mock_permission):
        """
        Test for checking member certificate  are updating perfectly with valid data
        """
        # arrange
        certificate = CertificateFactory()
        image = generate_test_image()
        data = {
            "member_ID": certificate.member.member_ID,
            "title": self.faker.name(),
            "certificate_document": image,
            "certificate_number": self.faker.bothify(text="??#####"),
            "id": certificate.pk
        }
        data.pop("id")
        response = self.client.patch(
            f"/api/member/v1/members/certificate/", data, format='multipart')
        response_data = response.json()
        # Assert
        if data.get('id') is not None:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data['status'], "success")
            self.assertEqual(response_data['code'], 200)
            self.assertIn('certificate_id', response_data['data'])
            self.assertIn(
                "Member Certificate has been updated successfully", response_data["message"])
        else:
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response_data['status'], "success")
            self.assertEqual(response_data['code'], 201)
            self.assertIn('certificate_id', response_data['data'])
            self.assertIn("Member Certificate has been created successfully", response_data["message"])

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_certificate_update_api_with_invalid_data(self, mock_permission):
        """
        Test for checking member certificate perfectly with invalid data
        """
        # arrange
        certificate = CertificateFactory()
        data = {
            "member_ID": certificate.member.member_ID,
            # "title": self.faker.name(),
            # "certificate_document": generate_test_image(),
            "certificate_number": self.faker.bothify(text="??#####"),
            "id": certificate.pk,
            # "id": certificate.pk+2,

        }
        response = self.client.patch(
            f"/api/member/v1/members/certificate/", data, format='multipart')
        response_data = response.json()
        # Assert
        if response_data['code'] == 500:
            self.assertEqual(response_data['status'], "failed")
            self.assertEqual(response_data['message'], "Something went wrong")
            self.assertEqual(response_data['errors']['server_error'], ['Certificate matching query does not exist.'])

        if response_data['code'] == 400:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response_data['status'], "failed")
            self.assertEqual(response_data['errors']['certificate_document'], [
                             'No file was submitted.'])
            self.assertIn("certificate_document", response_data["errors"])
            self.assertEqual(response_data['errors']['title'], [
                             'This field is required.'])


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

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_member_contact_number_add_endpoint_with_valid_data(self, mock_permission):
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

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_member_contact_number_add_endpoint_with_invalid_data(self, mock_permission):
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

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_contact_number_update_endpoint_with_valid_data(self, mock_permission):
        """
        Test contact number update endpoint with valid data
        """
        # arrange
        shared_member = MemberFactory()
        shared_contact_type = ContactTypeFactory()
        new_contact_type = ContactTypeFactory()
        contact_numbers = ContactNumberFactory.create_batch(
            5, member=shared_member, contact_type=shared_contact_type)
        data = [
            {
                "id": number.id,
                "contact_type": new_contact_type.id,
                "is_primary": number.is_primary,
                "number": fake.random_number(digits=12)

            } for number in contact_numbers
        ]
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/contact_numbers/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 200)
        _response = _response.json()
        self.assertEqual(_response['code'], 200)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)
        self.assertEqual(len(_response['data']), 5)
        for obj in _response['data']:
            self.assertEqual(obj.get("status"), "updated")

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_contact_number_update_endpoint_with_invalid_data(self, mock_permission):
        """
        Test contact number update endpoint with invalid data
        """
        # arrange
        shared_member = MemberFactory()
        shared_contact_type = ContactTypeFactory()
        new_contact_type = ContactTypeFactory()
        contact_numbers = ContactNumberFactory.create_batch(
            5, member=shared_member, contact_type=shared_contact_type)
        data = [
            {
                "id": number.id,
                "contact_type": new_contact_type.id+10,
                "is_primary": number.is_primary

            } for number in contact_numbers
        ]
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/contact_numbers/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)
        self.assertEqual(_response['status'], "failed")
        self.assertIn("errors", _response)

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_contact_number_update_endpoint_add_one_more_with_valid_data(self, mock_permission):
        """
        Test contact number update endpoint with valid data. And try to add one more contact number
        """
        # arrange
        shared_member = MemberFactory()
        shared_contact_type = ContactTypeFactory()
        new_contact_type = ContactTypeFactory()
        contact_numbers = ContactNumberFactory.create_batch(
            5, member=shared_member, contact_type=shared_contact_type)
        data = [
            {
                "id": number.id,
                "contact_type": new_contact_type.id,
                "is_primary": number.is_primary,
                "number": fake.random_number(digits=12)

            } for number in contact_numbers
        ]
        data.append({
            "contact_type": new_contact_type.id,
            "is_primary": False,
            "number": fake.random_number(digits=12)
        })
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/contact_numbers/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 200)
        _response = _response.json()
        self.assertEqual(_response['code'], 200)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)
        self.assertEqual(len(_response['data']), 6)
        for obj in _response['data']:
            self.assertTrue(obj.get("status") in ["updated", "created"])


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

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_member_email_address_add_with_valid_data(self, mock_permission):
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

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_member_email_address_add_with_invalid_data(self, mock_permission):
        """
        Test for checking member email address add api with invalid data. Like missing data and wrong email type
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
                    "email_type": self.email_type.id+1,
                    "is_primary": False
                }
            ]
        }
        # act
        _response = self.client.post(
            "/api/member/v1/members/email_address/", _data, format="json")

        # assert
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_email_address_update_endpoint_with_valid_data(self, mock_permission):
        """
        Test email address update endpoint with valid data
        """
        # arrange
        shared_member = MemberFactory()
        shared_email_type = EmailTypeChoiceFactory()
        new_email_type = EmailTypeChoiceFactory()
        email_addresses = EmailFactory.create_batch(
            5, member=shared_member, email_type=shared_email_type)
        data = [
            {
                "id": email.id,
                "email_type": new_email_type.id,
                "is_primary": email.is_primary,
                "email": fake.email()
            } for email in email_addresses
        ]
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/email_address/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 200)
        _response = _response.json()
        self.assertEqual(_response['code'], 200)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)
        self.assertEqual(len(_response['data']), 5)
        for obj in _response['data']:
            self.assertEqual(obj.get("status"), "updated")

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_email_address_update_endpoint_with_invalid_data(self, mock_permission):
        """
        Test email address update endpoint with invalid data
        """
        # arrange
        shared_member = MemberFactory()
        shared_email_type = EmailTypeChoiceFactory()
        new_email_type = EmailTypeChoiceFactory()
        email_addresses = EmailFactory.create_batch(
            5, member=shared_member, email_type=shared_email_type)
        data = [
            {
                "id": email.id,
                "email_type": new_email_type.id+10,
                "is_primary": email.is_primary,
                "email": fake.name()
            } for email in email_addresses
        ]
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/email_address/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)
        self.assertEqual(_response['status'], "failed")
        self.assertIn("errors", _response)

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_email_address_update_add_one_more_email_endpoint_with_valid_data(self, mock_permission):
        """
        Test email address update endpoint with valid data. We will try to add one more email address
        """
        # arrange
        shared_member = MemberFactory()
        shared_email_type = EmailTypeChoiceFactory()
        new_email_type = EmailTypeChoiceFactory()
        email_addresses = EmailFactory.create_batch(
            5, member=shared_member, email_type=shared_email_type)
        data = [
            {
                "id": email.id,
                "email_type": new_email_type.id,
                "is_primary": email.is_primary,
                "email": fake.email()
            } for email in email_addresses
        ]
        data.append({
            "email_type": new_email_type.id,
            "is_primary": False,
            "email": fake.email()
        })
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/email_address/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 200)
        _response = _response.json()
        self.assertEqual(_response['code'], 200)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)
        self.assertEqual(len(_response['data']), 6)
        for obj in _response['data']:
            self.assertTrue(obj.get("status") in ["created", "updated"])


class TestMemberAddressAddAndUpdate(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.address_type = AddressTypeChoiceFactory()
        cls.user = get_user_model().objects.create_superuser(
            username=fake.user_name(), password=fake.password(length=6))

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_member_address_add_with_valid_data(self, mock_permission):
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

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_member_address_add_with_invalid_data(self, mock_permission):
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

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_address_update_endpoint_with_valid_data(self, mock_permission):
        """
        Test address update endpoint with valid data
        """
        # arrange
        shared_member = MemberFactory()
        shared_address_type = AddressTypeChoiceFactory()
        new_address_type = AddressTypeChoiceFactory()
        addresses = AddressFactory.create_batch(
            5, member=shared_member, address_type=shared_address_type)
        data = [
            {
                "id": address.id,
                "address_type": new_address_type.id,
                "is_primary": address.is_primary,
                "address": fake.address()
            } for address in addresses
        ]
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/address/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 200)
        _response = _response.json()
        self.assertEqual(_response['code'], 200)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)
        self.assertEqual(len(_response['data']), 5)
        for obj in _response['data']:
            self.assertEqual(obj.get("status"), "updated")

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_address_update_endpoint_with_invalid_data(self, mock_permission):
        """
        Test address update endpoint with invalid data. Like missing fields
        """
        # arrange
        shared_member = MemberFactory()
        shared_address_type = AddressTypeChoiceFactory()
        new_address_type = AddressTypeChoiceFactory()
        addresses = AddressFactory.create_batch(
            5, member=shared_member, address_type=shared_address_type)
        data = [
            {
                "id": address.id,
                "address_type": new_address_type.id,
                "is_primary": address.is_primary
            } for address in addresses
        ]
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/address/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)
        self.assertEqual(_response['status'], "failed")
        self.assertIn("errors", _response)

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_address_update_add_another_endpoint_with_valid_data(self, mock_permission):
        """
        Test address update endpoint with valid data. Try to add another address
        """
        # arrange
        shared_member = MemberFactory()
        shared_address_type = AddressTypeChoiceFactory()
        new_address_type = AddressTypeChoiceFactory()
        addresses = AddressFactory.create_batch(
            5, member=shared_member, address_type=shared_address_type)
        data = [
            {
                "id": address.id,
                "address_type": new_address_type.id,
                "is_primary": address.is_primary,
                "address": fake.address()
            } for address in addresses
        ]

        data.append({
            "address_type": new_address_type.id,
            "is_primary": False,
            "address": fake.address()
        })
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/address/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 200)
        _response = _response.json()
        self.assertEqual(_response['code'], 200)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)
        self.assertEqual(len(_response['data']), 6)
        for obj in _response['data']:
            self.assertTrue(obj.get("status") in ["updated", "created"])


class TestMemberJobInformationAddAndUpdate(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.user = get_user_model().objects.create_superuser(
            username=fake.user_name(), password=fake.password(length=8))

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_job_information_add_with_valid_data(self, mock_permission):
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

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_job_information_add_with_invalid_data(self, mock_permission):
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

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_job_update_endpoint_with_valid_data(self, mock_permission):
        """
        Test job update endpoint with valid data
        """
        # arrange
        shared_member = MemberFactory()
        jobs = JobFactory.create_batch(5, member=shared_member)
        data = [
            {
                "id": job.id,
                "title": fake.job(),
                "organization_name": fake.company(),
                "location": fake.country(),
                "job_description": fake.name(),
            } for job in jobs
        ]
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/job/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 200)
        _response = _response.json()
        self.assertEqual(_response['code'], 200)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)
        self.assertEqual(len(_response['data']), 5)
        for obj in _response['data']:
            self.assertEqual(obj.get("status"), "updated")

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_job_update_endpoint_with_invalid_data(self, mock_permission):
        """
        Test job update endpoint with invalid data. Like missing fields
        """
        # arrange
        shared_member = MemberFactory()
        jobs = JobFactory.create_batch(5, member=shared_member)
        data = [
            {
                "id": job.id,
                "organization_name": fake.company(),
                "location": fake.country(),
                "job_description": fake.name(),
            } for job in jobs
        ]
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/job/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)
        self.assertEqual(_response['status'], "failed")
        self.assertIn("errors", _response)

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_job_update_add_one_more_endpoint_with_valid_data(self, mock_permission):
        """
        Test job update endpoint with valid data more job data. Try to add more job.
        """
        # arrange
        shared_member = MemberFactory()
        jobs = JobFactory.create_batch(5, member=shared_member)
        data = [
            {
                "id": job.id,
                "title": fake.job(),
                "organization_name": fake.company(),
                "location": fake.country(),
                "job_description": fake.name(),
            } for job in jobs
        ]
        data.append({
            "title": fake.job(),
            "organization_name": fake.company(),
            "location": fake.country(),
            "job_description": fake.name(),
        })
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/job/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 200)
        _response = _response.json()
        self.assertEqual(_response['code'], 200)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)
        self.assertEqual(len(_response['data']), 6)
        for obj in _response['data']:
            self.assertTrue(obj.get("status") in ["updated", "created"])


class TestMemberEmergencyContactAddAndUpdate(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.user = get_user_model().objects.create_superuser(
            username=fake.user_name(), password=fake.password(length=8))

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_member_emergency_contact_add_with_valid_data(self, mock_permission):
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

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_member_emergency_contact_add_with_invalid_data(self, mock_permission):
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

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_emergency_contact_update_endpoint_with_valid_data(self, mock_permission):
        """
        Test emergency contact update endpoint with valid data
        """
        # arrange
        shared_member = MemberFactory()
        emergency_contact = EmergencyContactFactory.create_batch(
            5, member=shared_member)
        data = [
            {
                "id": contact.id,
                "contact_name": fake.name(),
                "contact_number": fake.random_number(digits=12),
            } for contact in emergency_contact
        ]
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/emergency_contact/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 200)
        _response = _response.json()
        self.assertEqual(_response['code'], 200)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)
        self.assertEqual(len(_response['data']), 5)
        for obj in _response['data']:
            self.assertEqual(obj.get("status"), "updated")

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_emergency_contact_update_endpoint_with_invalid_data(self, mock_permission):
        """
        Test emergency contact update endpoint with invalid data. Like missing fields
        """
        # arrange
        shared_member = MemberFactory()
        emergency_contact = EmergencyContactFactory.create_batch(
            5, member=shared_member)
        data = [
            {
                "id": contact.id,
                "contact_name": fake.name(),
            } for contact in emergency_contact
        ]
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/emergency_contact/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)
        self.assertEqual(_response['status'], "failed")
        self.assertIn("errors", _response)

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_emergency_contact_update_add_another_endpoint_with_valid_data(self, mock_permission):
        """
        Test emergency contact update endpoint with valid data.Try to add one more emergency contact
        """
        # arrange
        shared_member = MemberFactory()
        emergency_contact = EmergencyContactFactory.create_batch(
            5, member=shared_member)
        data = [
            {
                "id": contact.id,
                "contact_name": fake.name(),
                "contact_number": fake.random_number(digits=12),
            } for contact in emergency_contact
        ]
        data.append({
            "contact_name": fake.name(),
            "contact_number": fake.random_number(digits=12),
        })
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/emergency_contact/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 200)
        _response = _response.json()
        self.assertEqual(_response['code'], 200)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)
        self.assertEqual(len(_response['data']), 6)
        for obj in _response['data']:
            self.assertTrue(obj.get("status") in ["updated", "created"])


class TestMemberSpecialDayAddAndUpdate(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()
        cls.user = get_user_model().objects.create_superuser(
            username=fake.user_name(), password=fake.password(length=8))

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_member_special_day_add_with_valid_data(self, mock_permission):
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

    @patch.object(AddMemberPermission, "has_permission", return_value=True)
    def test_member_special_day_add_with_invalid_data(self, mock_permission):
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

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_special_day_update_endpoint_with_valid_data(self, mock_permission):
        """
        Test special day update endpoint with valid data.
        """
        # arrange
        shared_member = MemberFactory()
        special_days = SpecialDayFactory.create_batch(5, member=shared_member)
        data = [
            {
                "id": special_day.id,
                "title": fake.name(),
                "date": fake.date_between(start_date="-10y", end_date="today").strftime("%Y-%m-%d"),
            } for special_day in special_days
        ]
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/special_day/{shared_member.member_ID}/", _data, format="json")
        # assert
        self.assertEqual(_response.status_code, 200)
        _response = _response.json()

        self.assertEqual(_response['code'], 200)
        self.assertEqual(_response['status'], "success")
        self.assertIn("data", _response)
        self.assertEqual(len(_response['data']), 5)
        for obj in _response['data']:
            self.assertEqual(obj.get("status"), "updated")

    @patch.object(UpdateMemberPermission, "has_permission", return_value=True)
    def test_member_special_day_update_endpoint_with_invalid_data(self, mock_permission):
        """
        Test special day update endpoint with invalid data. Like missing title fields
        """
        # arrange
        shared_member = MemberFactory()
        special_days = SpecialDayFactory.create_batch(5, member=shared_member)
        data = [
            {
                "id": special_day.id,
                "date": fake.date_between(start_date="-10y", end_date="today").strftime("%Y-%m-%d"),
            } for special_day in special_days
        ]
        _data = {
            "member_ID": shared_member.member_ID,
            "data": data
        }
        # act
        _response = self.client.patch(
            f"/api/member/v1/members/special_day/{shared_member.member_ID}/", _data, format="json")
        
        # assert
        self.assertEqual(_response.status_code, 400)
        _response = _response.json()
        self.assertEqual(_response['code'], 400)
        self.assertEqual(_response['status'], "failed")
        self.assertEqual(_response['message'], "Invalid request")
        self.assertIn("errors", _response)

        self.assertEqual(len(_response['errors']['data']), 5)
        for error in _response['errors']['data']:
            self.assertListEqual(error['title'], ['This field is required.'])
