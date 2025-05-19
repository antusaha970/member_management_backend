

from django.contrib import admin
from django.apps import apps

app_name = "facility"
models_list = apps.get_app_config(app_name).get_models()

for model in models_list:
    class DynamicAdmin(admin.ModelAdmin):
        list_display = [field.name for field in model._meta.fields]
        
    try:
        admin.site.register(model, DynamicAdmin)
    except admin.sites.AlreadyRegistered:
        pass
