from django.contrib import admin
from .models import OTP, CustomUser, AccountTestModel,PermissonModel
from django.contrib.auth.models import Group,Permission

admin.site.register(OTP)
admin.site.register(CustomUser)
admin.site.register(AccountTestModel)
admin.site.register(PermissonModel)
