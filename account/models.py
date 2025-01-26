from django.db import models
# from django.contrib.auth import get_user_model
from club.models import Club
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class OTP(models.Model):
    otp = models.IntegerField()
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_otp")

    def __str__(self):
        return self.user.username


class CustomUser(AbstractUser):
    club = models.ForeignKey(
        Club, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username
