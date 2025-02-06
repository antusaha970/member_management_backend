from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from account.models import PermissonModel, GroupModel, AssignGroupPermission
from club.models import Club
import pdb


class CustomPermissionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin", password="admin")
        self.normal_user = get_user_model().objects.create_user(
            username="salauddin_85", password="root25809#")
        self.permission1 = PermissonModel.objects.create(name="add_member")
        self.permission2 = PermissonModel.objects.create(name="view_member")
        # API endpoint
        self.url = "/api/account/v1/authorization/custom_permission_name/"

    def test_create_permission_success(self):
        admin = self.client.force_authenticate(user=self.admin_user)
        # print(admin.is_superuser)
        data = {"name": "add_member_permission"}
        response = self.client.post(self.url, data)
        succes = self.assertEqual(
            response.status_code, status.HTTP_201_CREATED)
        ids = self.assertIn("id", response.data)
        name = self.assertIn("permission_name", response.data)
        self.assertEqual(
            response.data["permission_name"], "add_member_permission")

    def test_create_permission_unauthenticated(self):
        """Test that unauthenticated users cannot create permissions and check error message"""
        data = {"name": "view_permission"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_create_permission_non_admin(self):
        """Test that a normal user (non-admin) cannot create permissions and validate response"""
        self.client.force_authenticate(user=self.normal_user)
        data = {"name": "view_member"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)

    def test_create_permission_duplicate_name(self):
        """Test that duplicate permission names are not allowed"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "add_member"}  # Already exists
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
        self.assertGreaterEqual(len(response.data), 2)
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


class CustomGroupModel(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin", password="admin")
        self.normal_user = get_user_model().objects.create_user(
            username="salauddin_85", password="root25809#")

        self.club = Club.objects.create(name="golpokotha")
        self.groupname = GroupModel.objects.create(name="test", club=self.club)
        self.permission1 = PermissonModel.objects.create(name="add_member")
        self.permission2 = PermissonModel.objects.create(name="view_member")
        self.admin_user.club = self.club
        self.url = "/api/account/v1/authorization/group_permissions/"

    def test_create_group_success(self):
        """Ensure that an admin user can create a group with permissions"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "moderator", "permission": [
            self.permission1.id, self.permission2.id], "club": 1}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("group_id", response.data)
        self.assertIn("name", response.data)
        self.assertEqual(response.data["permission"], [
                         self.permission1.id, self.permission2.id])
        group_exists = GroupModel.objects.filter(name="moderator").exists()
        self.assertTrue(group_exists)

    def test_create_group_without_permissions(self):
        """ Ensure a group cannot be created without permissions"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "moderator", "permission": [], "club": self.club.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(GroupModel.objects.filter(name="moderator").exists())

    def test_create_group_with_invalid_permission(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "moderator", "permission": [
            "dskk"], "club": self.club.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_group_without_club(self):
        """ Ensure an error occurs when no club is provided"""
        self.client.force_authenticate(user=self.admin_user)
        data = {"name": "team_lead", "permission": [self.permission1.id]}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)

    def test_create_group_with_long_name(self):
        """ Ensure group name does not exceed max length"""
        self.client.force_authenticate(user=self.admin_user)
        long_name = "A" * 300
        data = {"name": long_name, "permission": [
            self.permission1.id], "club": self.club.id}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)

    def test_get_groups(self):
        """ Test fetching groups for a user"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("data" in response.data)

    def test_patch_group(self):
        """Test updating a group"""
        self.client.force_authenticate(user=self.admin_user)
        group_id = self.groupname.id
        url = f"{self.url}{group_id}/"

        payload = {"name": "updated_moderator", "permission": [
            self.permission1.id], "club": self.club.id}
        response = self.client.patch(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.groupname.refresh_from_db()
        self.assertEqual(self.groupname.name, "updated_moderator")

    def test_delete_group(self):
        """ Test deleting a group"""
        self.client.force_authenticate(user=self.normal_user)
        group_id = self.groupname.id
        url = f"{self.url}{group_id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(GroupModel.objects.filter(
            id=self.groupname.id).exists())
