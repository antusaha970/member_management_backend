from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from ..models import PermissonModel  

class CustomPermissionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(username="admin", password="adminpass")
        self.normal_user = get_user_model().objects.create_user(username="user", password="userpass")
        self.permission1 = PermissonModel.objects.create(name="Read Access")
        self.permission2 = PermissonModel.objects.create(name="Write Access")

        # API endpoint
        self.url = "api/account/v1/authorization/custom_permission_name/"

    def test_create_permission_success(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "Delete Access"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("permission_name", response.data)
        self.assertEqual(response.data["permission_name"], "Delete Access")

    def test_create_permission_unauthenticated(self):
        """Test that unauthenticated users cannot create permissions and check error message"""
        data = {"name": "Manage Users"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_create_permission_non_admin(self):
        """Test that a normal user (non-admin) cannot create permissions and validate response"""
        self.client.force_authenticate(user=self.normal_user)
        data = {"name": "Manage Users"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)

    def test_create_permission_duplicate_name(self):
        """Test that duplicate permission names are not allowed"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "Read Access"}  # Already exists
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
        self.assertIn("name", response.data["errors"])

    def test_create_permission_empty_name(self):
        """Test that an empty permission name is not allowed"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": ""}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
        self.assertIn("name", response.data["errors"])

    def test_get_all_permissions(self):
        """Test fetching all permissions and check response data structure"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 2)  # We created 2 permissions in setUp()
        for permission in response.data:
            self.assertIn("id", permission)
            self.assertIn("name", permission)

    def test_get_permissions_unauthenticated(self):
        """Test that an unauthenticated user cannot fetch permissions"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_get_permissions_non_admin(self):
        """Test that a non-admin user cannot fetch permissions"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
