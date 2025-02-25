from django.contrib import admin
from . import models

admin.site.register(models.Gender)
admin.site.register(models.MembershipType)
admin.site.register(models.InstituteName)
admin.site.register(models.MembershipStatusChoice)
admin.site.register(models.MaritalStatusChoice)
admin.site.register(models.EmailTypeChoice)
admin.site.register(models.SpouseStatusChoice)
admin.site.register(models.DescendantRelationChoice)
admin.site.register(models.DocumentTypeChoice)
