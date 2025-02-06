from rest_framework.test import APITestCase
from faker import Faker
from club.models import Club
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


class AuthenticationAPITest(APITestCase):
    def setUp(self):
        self.faker = Faker()
        # setup club
        self.club = Club.objects.create(name=self.faker.name())

    def test_registration_api_with_valid_data(self):
        """
          Endpoint: /api/account/v1/register/  
        """
        # Arrange
        name = self.faker.name()
        email = self.faker.email()
        username = self.faker.user_name()
        password = self.faker.password(length=8)
        club = self.club.id
        remember_me = self.faker.boolean(chance_of_getting_true=50)
        _data = {
            'name': name,
            'email': email,
            'username': username,
            'password': password,
            'club': club,
            'remember_me': remember_me
        }

        # Act
        _response = self.client.post("/api/account/v1/register/", data=_data)

        # Assert
        self.assertEqual(_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", _response.json())

    def test_login_api_with_valid_data(self):
        """
            Endpoint: /api/account/v1/login/
        """

        # Arrange
        username = self.faker.user_name()
        password = self.faker.password(length=8)
        user = get_user_model().objects.create_user(
            username=username, password=password)
        _data = {
            'username': username,
            'password': password,
            'remember_me': self.faker.boolean(chance_of_getting_true=50)
        }

        # Act
        _response = self.client.post("/api/account/v1/login/", data=_data)

        # Assert
        response_data = _response.json()
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response_data)
        self.assertEqual('success', response_data['status'])

    def test_login_api_with_invalid_data(self):
        """
            Endpoint: /api/account/v1/login/
        """

        # Arrange
        username = self.faker.user_name()
        password = self.faker.password(length=8)
        user = get_user_model().objects.create_user(
            username=username, password=password)
        _data = {
            'username': self.faker.user_name(),
            'password': password,
            'remember_me': self.faker.boolean(chance_of_getting_true=50)
        }

        # Act
        _response = self.client.post("/api/account/v1/login/", data=_data)

        # Assert
        response_data = _response.json()
        self.assertEqual(_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response_data)
        self.assertEqual('failed', response_data['status'])

    def test_logout_api_with_valid_token(self):
        """
            Endpoint: /api/account/v1/logout/
        """

        # Arrange
        username = self.faker.user_name()
        password = self.faker.password(length=8)
        user = get_user_model().objects.create_user(
            username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)

        # act
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {str(token)}")
        _response = self.client.delete("/api/account/v1/logout/")
        auth_cookie = _response.cookies.get("auth_token")

        # Assert
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        if auth_cookie:  # Check if the auth_token cookie is deleted or expired
            self.assertEqual(auth_cookie.value, "")
        else:
            self.assertIsNone(auth_cookie)

    def test_logout_api_with_invalid_token(self):
        """
            Endpoint: /api/account/v1/logout/
        """

        # Arrange
        username = self.faker.user_name()
        password = self.faker.password(length=8)
        user = get_user_model().objects.create_user(
            username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)

        # act
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {str(token)}f")
        _response = self.client.delete("/api/account/v1/logout/")

        # Assert
        self.assertEqual(_response.status_code, status.HTTP_401_UNAUTHORIZED)
