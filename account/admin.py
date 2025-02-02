from django.contrib import admin
from .models import OTP, CustomUser, AccountTestModel, PermissonModel, GroupModel, AssignGroupPermission

admin.site.register(OTP)
admin.site.register(CustomUser)

admin.site.register(AccountTestModel)
admin.site.register(PermissonModel)
admin.site.register(GroupModel)
admin.site.register(AssignGroupPermission)