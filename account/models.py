from django.db import models
from django.contrib.auth.models import User


class OTP(models.Model):
    otp = models.IntegerField()
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_otp")

    def __str__(self):
        return self.user.username
