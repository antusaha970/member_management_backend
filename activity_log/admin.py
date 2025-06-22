from django.contrib import admin
from .models import ActivityLog

# Get all field names
activity_log_fields = [field.name for field in ActivityLog._meta.fields]

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = activity_log_fields

admin.site.register(ActivityLog, ActivityLogAdmin)
