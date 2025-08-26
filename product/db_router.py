class SecondaryRouter:
    SECONDARY_APPS = ['product', 'facility']

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
