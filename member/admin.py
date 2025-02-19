from django.contrib import admin
from . import models

admin.site.register(models.Member)
admin.site.register(models.MembersFinancialBasics)

admin.site.register(models.Address)

admin.site.register(models.Descendant)
admin.site.register(models.Certificate)

admin.site.register(models.ContactNumber)
admin.site.register(models.Profession)
admin.site.register(models.CompanionInformation)
admin.site.register(models.SpecialDay)
admin.site.register(models.Spouse)
admin.site.register(models.EmergencyContact)
admin.site.register(models.Documents)
admin.site.register(models.AvailableID)
admin.site.register(models.MemberHistory)
