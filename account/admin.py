from django.contrib import admin
from .models import OTP, CustomUser

admin.site.register(OTP)
admin.site.register(CustomUser)
