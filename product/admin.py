from django.contrib import admin
from django.utils.html import format_html
from .models import ProductMedia
from django.apps import apps

# Custom Admin class for ProductMedia
class ProductMediaAdmin(admin.ModelAdmin):
    def image_tag(self, obj):
        return format_html(
            '<img src="{}" style="max-width:200px; max-height:200px"/>'.format(obj.image.url)
        )
    image_tag.short_description = 'Image Preview'

    list_display = ['id', 'product', 'image_tag'] 
    list_display_links = ['id', 'product']  


# Register ProductMedia with custom admin
admin.site.register(ProductMedia, ProductMediaAdmin)

# Register all other models dynamically, excluding ProductMedia
app_name = "product"
models = apps.get_app_config(app_name).get_models()

for model in models:
    if model != ProductMedia:
        class DynamicAdmin(admin.ModelAdmin):
            list_display = [field.name for field in model._meta.fields]
        try:
            admin.site.register(model, DynamicAdmin)
        except admin.sites.AlreadyRegistered:
            pass

