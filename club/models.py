from django.db import models


class Club(models.Model):
    name = models.CharField(max_length=500, unique=True)

    # record keeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
