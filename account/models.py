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


class AccountTestModel(models.Model):
    name = models.TextField()


# authorization Model


class PermissonModel(models.Model):
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name


class GroupModel(models.Model):
    name = models.CharField(max_length=250, unique=True)
    permission = models.ManyToManyField(PermissonModel)

    def __str__(self):
        return self.name


class AssignGroupPermission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             related_name="custom_user", null=True, blank=True)
    group = models.ManyToManyField(GroupModel)

    def __str__(self):
        groups_all = self.group.all()
        group_name = ""
        for grp in groups_all:
            group_name = group_name + f"{grp}"
        return f"{self.user} - {group_name}"


class OTP(models.Model):
    otp = models.IntegerField()
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class VerifySuccessfulEmail(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
