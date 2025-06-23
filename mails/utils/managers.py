from django.db import models

class EmailListManager(models.Manager):
    def active(self):
        return self.filter(is_subscribed=True)
    
    def inactive(self):
        return self.filter(is_subscribed=False)

    def by_email(self, email):
        return self.filter(email=email)

    def search_name(self, name):
        return self.filter(full_name__icontains=name)
