from django.contrib import admin
from .models import OTP, CustomUser, ForgetPasswordOTP, PermissonModel, GroupModel, AssignGroupPermission

admin.site.register(ForgetPasswordOTP)
admin.site.register(OTP)
admin.site.register(CustomUser)

admin.site.register(PermissonModel)
admin.site.register(GroupModel)
admin.site.register(AssignGroupPermission)
