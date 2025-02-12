from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from faker import Faker
import pdb
from ..models import ActivityLog
from django.utils import timezone
from unittest.mock import patch
from ..utils.permission_classes import AllUserActivityLogPermission


class TestForActivityLog(APITestCase):
    def setUp(self):
        self.faker = Faker()
        username = self.faker.user_name()
        password = self.faker.password()
        self.user = get_user_model().objects.create(
            username=username, password=password)

        # Create fake activity logs for this user
        for _ in range(200):  # Create 5 fake logs
            ActivityLog.objects.create(
                user=self.user,
                ip_address=self.faker.ipv4(),
                location={"city": self.faker.city(
                ), "country": self.faker.country()},
                user_agent=self.faker.user_agent(),
                request_method=self.faker.random_element(
                    ["GET", "POST", "PUT", "DELETE"]),
                severity_level=self.faker.random_element(
                    ["info", "warning", "error", "critical"]),
                referrer_url=self.faker.url(),
                device=self.faker.word() + " Device",
                path=self.faker.uri_path(),
                verb=self.faker.sentence(),
                description=self.faker.text(),
                timestamp=timezone.make_aware(self.faker.date_time_this_year())
            )

    def test_single_user_activity_log_api_with_valid_user(self):
        """
        Testing single user activity log for multiple pages with valid user
        """
        # arrange
        self.client.force_authenticate(user=self.user)

        # act
        _response = self.client.get(
            "/api/activity_log/v1/activity/user_activity/")

        # assert
        self.assertEqual(_response.status_code, 200)
        _response = _response.json()

        data = _response.get("data")
        self.assertEqual(len(data), 100)

        _response = self.client.get(
            "/api/activity_log/v1/activity/user_activity/?page=2")

        self.assertEqual(_response.status_code, 200)
        _response = _response.json()

        data = _response.get("data")
        self.assertEqual(len(data), 100)

    def test_single_user_activity_log_api_with_invalid_user(self):
        """
            Testing activity_log_api_with_invalid_user 
        """
        # arrange
        user = get_user_model().objects.create(username=self.faker.user_name(),
                                               password=self.faker.password(length=8))
        self.client.force_authenticate(user=user)

        # act
        _response = self.client.get(
            "/api/activity_log/v1/activity/user_activity/")

        # assert
        self.assertEqual(_response.status_code, 404)
        _response = _response.json()

        data = _response.get("data")
        self.assertEqual(len(data), 0)

    @patch.object(AllUserActivityLogPermission, "has_permission", return_value=True)
    def test_all_user_activity_log_api_with_valid_user(self, mock_permission):
        """
        Test all user activity with an user who has the permission

        """

        # arrange
        admin = get_user_model().objects.create_superuser(
            username=self.faker.user_name(), password=self.faker.password(length=8))
        self.client.force_authenticate(user=admin)

        # act
        _response = self.client.get(
            "/api/activity_log/v1/activity/all_user_activity/")

        # assert

        self.assertEqual(_response.status_code, 200)
        _response = _response.json()

        data = _response.get("data")
        self.assertEqual(len(data), 100)

        _response = self.client.get(
            "/api/activity_log/v1/activity/all_user_activity/?page=2")

        self.assertEqual(_response.status_code, 200)
        _response = _response.json()

        data = _response.get("data")
        self.assertEqual(len(data), 100)

    @patch.object(AllUserActivityLogPermission, "has_permission", return_value=False)
    def test_all_user_activity_log_api_with_invalid_user(self, mock_permission):
        """
        Test all user activity with an user who don't have the permission

        """

        # arrange
        admin = get_user_model().objects.create_superuser(
            username=self.faker.user_name(), password=self.faker.password(length=8))
        self.client.force_authenticate(user=admin)

        # act
        _response = self.client.get(
            "/api/activity_log/v1/activity/all_user_activity/")

        # assert

        self.assertEqual(_response.status_code, 403)
        _response = _response.json()
        self.assertIn("errors", _response)
