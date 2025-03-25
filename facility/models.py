from django.db import models
from member.models import MembershipType


class Facility(models.Model):
    FACILITY_STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    USAGES_ROLES_CHOICES = [
        ('member', 'Member'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
    ]

    name = models.CharField(max_length=255,unique=True)
    description = models.TextField()
    usages_fee = models.DecimalField(max_digits=10, decimal_places=2)
    usages_roles = models.CharField(max_length=50,choices=USAGES_ROLES_CHOICES,default="member") 
    operating_hours = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=FACILITY_STATUS_CHOICES, default='open')
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class FacilityUseFee(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.RESTRICT)
    membership_type = models.ForeignKey(MembershipType, on_delete=models.RESTRICT)
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Fee {self.fee} for {self.facility.name} "
