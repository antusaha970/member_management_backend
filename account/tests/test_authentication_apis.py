from rest_framework.test import APITestCase
from faker import Faker
from club.models import Club
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import ForgetPasswordOTP


class AuthenticationAPITest(APITestCase):
    def setUp(self):
        self.faker = Faker()
        # setup club
        self.club = Club.objects.create(name=self.faker.name())

    def test_registration_api_with_valid_data(self):
        """
          Endpoint: /api/account/v1/register/  
          Registration api with valid data and must return 201
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
        self.assertIn("access_token", _response.json())
        self.assertIn("refresh_token", _response.json())

    def test_login_api_with_valid_data(self):
        """
            Endpoint: /api/account/v1/login/
            Login with valid data and must return 200 and a token
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
        self.assertIn('access_token', response_data)
        self.assertIn('refresh_token', response_data)
        self.assertEqual('success', response_data['status'])

    def test_login_api_with_invalid_data(self):
        """
            Endpoint: /api/account/v1/login/
            Login with invalid data and must not return a token
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
        self.assertNotIn('access_token', response_data)
        self.assertNotIn('refresh_token', response_data)
        self.assertEqual('failed', response_data['status'])

    def test_logout_api_with_valid_token(self):
        """
            Endpoint: /api/account/v1/logout/
            Logout with valid token and must be auth_token cookie can't have value
        """

        # Arrange
        username = self.faker.user_name()
        password = self.faker.password(length=8)
        user = get_user_model().objects.create_user(
            username=username, password=password)
        token = RefreshToken.for_user(user)

        # act
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        _response = self.client.delete("/api/account/v1/logout/")
        auth_cookie = _response.cookies.get("access_token")
        refresh_cookie = _response.cookies.get("refresh_token")

        # Assert
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        if auth_cookie:  # Check if the auth_token cookie is deleted or expired
            self.assertEqual(auth_cookie.value, "")
        else:
            self.assertIsNone(auth_cookie)
        if refresh_cookie:
            self.assertEqual(refresh_cookie.value, "")
        else:
            self.assertIsNone(refresh_cookie)


class ResetPasswordAPITest(APITestCase):
    def setUp(self):
        self.faker = Faker()
        # setup club
        self.club = Club.objects.create(name=self.faker.name())
        username = self.faker.user_name()
        password = self.faker.password(length=8)
        self.email = "antusaha990@gmail.com"
        self.user = get_user_model().objects.create_user(
            username=username, password=password, email=self.email)
        self.user.club = self.club
        self.user.save()

    def test_forget_password_api_with_valid_email(self):
        """
            Endpoint : /api/account/v1/forget_password/
            check if OTP is going with valid email 
        """
        # arrange
        _data = {
            'email': self.email
        }

        # Act
        _response = self.client.post(
            "/api/account/v1/forget_password/", data=_data)

        # assert
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        self.assertEqual('success', _response.json()['status'])

    def test_forget_password_api_with_invalid_email(self):
        """
            Endpoint : /api/account/v1/forget_password/
            check if OTP is not going with invalid email
        """
        # arrange
        _data = {
            'email': self.faker.email()
        }

        # Act
        _response = self.client.post(
            "/api/account/v1/forget_password/", data=_data)

        # assert
        self.assertEqual(_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('failed', _response.json()['status'])

    def test_verify_otp_endpoint_with_valid_otp(self):
        """
            Endpoint: /api/account/v1/verify_otp/
            Test the OTP verification with valid OTP
        """

        # arrange
        email = self.email
        otp = self.faker.random_number(digits=4)
        token = self.faker.pystr(max_chars=20, min_chars=20)
        obj = ForgetPasswordOTP.objects.create(
            email=email, otp=otp, token=token)

        # act
        _data = {
            'email': email,
            'otp': otp,
        }
        _response = self.client.post("/api/account/v1/verify_otp/", data=_data)

        # assert
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        self.assertIn("token", _response.json())
        self.assertTrue(_response.json()['can_change_pass'])

    def test_verify_otp_endpoint_with_invalid_otp(self):
        """
            Endpoint: /api/account/v1/verify_otp/
            Test the OTP verification with invalid OTP
        """

        # arrange
        email = self.email
        otp = self.faker.random_number(digits=4)
        token = self.faker.pystr(max_chars=20, min_chars=20)
        obj = ForgetPasswordOTP.objects.create(
            email=email, otp=otp, token=token)

        # act
        _data = {
            'email': email,
            'otp': otp+1,
        }
        _response = self.client.post("/api/account/v1/verify_otp/", data=_data)

        # assert
        self.assertEqual(_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", _response.json())
        self.assertFalse(_response.json()['can_change_pass'])

    def test_reset_password_endpoint_with_valid_token(self):
        """
            Endpoint: /api/account/v1/reset_password/
            Test reset password with valid token provided
        """
        # Arrange
        email = self.email
        otp = self.faker.random_number(digits=4)
        token = self.faker.pystr(max_chars=20, min_chars=20)
        obj = ForgetPasswordOTP.objects.create(
            email=email, otp=otp, token=token)
        password = self.faker.password(length=8)
        _data = {
            'email': email,
            'password': password,
            'token': token
        }
        # act
        _response = self.client.post(
            "/api/account/v1/reset_password/", data=_data)

        # assert
        self.assertIn("access_token", _response.json())
        self.assertIn("refresh_token", _response.json())
        self.assertEqual(_response.status_code, status.HTTP_200_OK)

    def test_reset_password_endpoint_with_invalid_token(self):
        """
            Endpoint: /api/account/v1/reset_password/
            Test reset password with invalid token provided
        """
        # Arrange
        email = self.email
        otp = self.faker.random_number(digits=4)
        token = self.faker.pystr(max_chars=20, min_chars=20)
        obj = ForgetPasswordOTP.objects.create(
            email=email, otp=otp, token=token)
        password = self.faker.password(length=8)
        _data = {
            'email': email,
            'password': password,
            'token': f"{token}f"
        }
        # act
        _response = self.client.post(
            "/api/account/v1/reset_password/", data=_data)

        # assert
        self.assertNotIn("access_token", _response.json())
        self.assertNotIn("refresh_token", _response.json())
        self.assertEqual(_response.status_code, status.HTTP_400_BAD_REQUEST)
