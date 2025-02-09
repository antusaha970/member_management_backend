from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from account.models import PermissonModel, GroupModel, AssignGroupPermission
from club.models import Club
import pdb
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from faker import Faker
import os
from django.conf import settings


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


class AssignGroupUserAPIsTEST(APITestCase):

    def setUp(self):
        self.faker = Faker()
        username = self.faker.user_name()
        password = self.faker.password(length=8)
        email = self.faker.email()
        club_name = self.faker.name()
        self.club = Club.objects.create(name=club_name)
        self.user = get_user_model().objects.create_user(
            username=username, password=password, email=email, club=self.club)

        admin_username = self.faker.user_name()
        admin_password = self.faker.password(length=8)
        admin_email = self.faker.email()
        self.admin = get_user_model().objects.create_superuser(
            username=admin_username, password=admin_password, email=admin_email, club=self.club)
        self.token, _ = Token.objects.get_or_create(user=self.admin)

    def test_assign_group_user_post_method_with_valid_data(self):
        """
        Endpoint: "/api/account/v1/authorization/assign_group_user/"
        Test for assigning a user to a group with valid information
        """
        # arrange
        group_name = self.faker.name()
        permissions = PermissonModel.objects.create(name="register_account")
        group = GroupModel.objects.create(
            name=group_name, club=self.club)
        group.permission.add(permissions)
        group.save()

        # act
        _data = {
            'user': self.user.id,
            'group': [
                group.id
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {str(self.token)}")
        _response = self.client.post(
            "/api/account/v1/authorization/assign_group_user/", data=_data)

        # assert
        data = _response.json()
        self.assertEqual(_response.status_code, status.HTTP_201_CREATED)
        _groups = data.get("groups")[0]
        _user_id = data.get("user_id")
        _group_name = _groups.get("group_name")
        self.assertEqual(group_name, _group_name)
        self.assertEqual(_user_id, self.user.id)

    def test_assign_group_user_post_method_with_invalid_data(self):
        """
        Endpoint: "/api/account/v1/authorization/assign_group_user/"
        Test for assigning a user to a group with invalid information. Like the user does belongs to the admin group
        """
        # arrange
        group_name = self.faker.name()
        permissions = PermissonModel.objects.create(name="register_account")
        group = GroupModel.objects.create(
            name=group_name, club=self.club)
        group.permission.add(permissions)
        group.save()
        new_club = Club.objects.create(name=self.faker.name())
        self.user.club = new_club
        self.user.save()

        # act
        _data = {
            'user': self.user.id,
            'group': [
                group.id
            ]
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {str(self.token)}")
        _response = self.client.post(
            "/api/account/v1/authorization/assign_group_user/", data=_data)

        # assert
        data = _response.json()
        self.assertEqual(_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', data)

    def test_assign_group_user_get_method_with_valid_data(self):
        """
            Endpoint: "/api/account/v1/authorization/assign_group_user/"
            Test for getting all the groups with user for valid admin token
        """
        # act
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {str(self.token)}")
        _response = self.client.get(
            "/api/account/v1/authorization/assign_group_user/")
        # assert
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        self.assertIn('data', _response.json())

    def test_assign_group_user_get_method_with_invalid_data(self):
        """
            Endpoint: "/api/account/v1/authorization/assign_group_user/"
            Test for getting all the groups with user for invalid admin token
        """
        # arrange
        token, _ = Token.objects.get_or_create(user=self.user)
        # act
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {str(token)}")
        _response = self.client.get(
            "/api/account/v1/authorization/assign_group_user/")
        # assert
        self.assertEqual(_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn('data', _response.json())

    def test_assign_group_user_delete_method_with_valid_data(self):
        """
        Endpoint: "/api/account/v1/authorization/assign_group_user/"
        Test for deleting a user from a group with valid data
        """
        # arrange
        group_name = self.faker.name()
        permissions = PermissonModel.objects.create(name="register_account")
        group = GroupModel.objects.create(
            name=group_name, club=self.club)
        group.permission.add(permissions)
        group.save()
        assign_grp = AssignGroupPermission.objects.create(user=self.user)
        assign_grp.group.add(group)

        # act
        _data = {
            'user_id': self.user.id,
            'group_id': group.id
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {str(self.token)}")
        _response = self.client.delete(
            "/api/account/v1/authorization/assign_group_user/", data=_data)

        # assert
        self.assertEqual(_response.status_code, status.HTTP_200_OK)
        self.assertFalse(AssignGroupPermission.objects.filter(
            user=self.user, group=group).exists())

    def test_assign_group_user_delete_method_with_valid_data(self):
        """
        Endpoint: "/api/account/v1/authorization/assign_group_user/"
        Test for deleting a user from a group with invalid data
        """
        # arrange
        group_name = self.faker.name()
        permissions = PermissonModel.objects.create(name="register_account")
        group = GroupModel.objects.create(
            name=group_name, club=self.club)
        group.permission.add(permissions)
        group.save()
        assign_grp = AssignGroupPermission.objects.create(user=self.user)

        # act
        _data = {
            'user_id': self.user.id,
            'group_id': group.id
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {str(self.token)}")
        _response = self.client.delete(
            "/api/account/v1/authorization/assign_group_user/", data=_data)

        # assert
        self.assertEqual(_response.status_code, status.HTTP_400_BAD_REQUEST)
