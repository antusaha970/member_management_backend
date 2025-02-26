from rest_framework.test import APITestCase
from faker import Faker
from django.contrib.auth import get_user_model


class TestMemberCreateAndUpdateEndpoints(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """Creates test data once for the whole test class."""
        faker = Faker()
        cls.user = get_user_model().objects.create_superuser(
            username=faker.user_name(), password=faker.password(length=8))
