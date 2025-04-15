from django.contrib import admin

# Register your models here.
from django.apps import apps

app_name = "promo_code_app" 
models = apps.get_app_config(app_name).get_models()
for model in models:
    admin.site.register(model)
