from django.contrib import admin
from .models import OTP, CustomUser, AccountTestModel

admin.site.register(OTP)
admin.site.register(CustomUser)
admin.site.register(AccountTestModel)
