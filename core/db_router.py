
from django.apps import apps

SYSTEM_APPS = [
    'admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles'
]

class SecondaryRouter:
    SECONDARY_APPS = ['product', 'facility','member','core']
    # SECONDARY_APPS = [app.label for app in apps.get_app_configs() if app.label not in SYSTEM_APPS]


    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.SECONDARY_APPS:
            return 'secondary'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.SECONDARY_APPS:
            return 'secondary'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._meta.app_label in self.SECONDARY_APPS and
            obj2._meta.app_label in self.SECONDARY_APPS):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Migrations route
        if app_label in self.SECONDARY_APPS:
            return db == 'secondary'
        return None
