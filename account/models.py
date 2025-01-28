from django.db import models
# from django.contrib.auth import get_user_model
from club.models import Club
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Extend the user model with custom fields


class CustomUser(AbstractUser):
    club = models.ForeignKey(
        Club, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username

# Store user generated OTPS in the DB


class OTP(models.Model):
    otp = models.IntegerField()
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_otp")

    def __str__(self):
        return self.user.username


class AccountTestModel(models.Model):
    name = models.TextField()
