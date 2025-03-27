from django.contrib import admin
from django.apps import apps

app_name = "member_financial_management"
models = apps.get_app_config(app_name).get_models()


for model in models:
    admin.site.register(model)
