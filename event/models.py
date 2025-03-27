
from django.db import models
from member.models import Member
from django.contrib.auth import get_user_model
import pycountry
from member.models import MembershipType


COUNTRY_CHOICES = [(country.alpha_2, country.name)
                   for country in pycountry.countries]
COUNTRY_CHOICES.append(('XX', 'Unknown'))

EVENT_STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

EVENT_TICKET_STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold_out', 'Sold Out'),
        ('reserved', 'Reserved'),
        ('cancelled', 'Cancelled'),
    ]




class Venue(models.Model):
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state_province = models.CharField(max_length=255, blank=True,default="") 
    postal_code = models.CharField(max_length=20, blank=True,default="")  
    country = models.CharField(max_length=2,choices=COUNTRY_CHOICES)
    # record keeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('street_address', 'city', 'country')

    def __str__(self):
        return f"{self.street_address}, {self.city}"


class EventMedia(models.Model):
    image = models.ImageField(upload_to='event_photos/')
    
    # record keeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Event Media {self.id}"


class Event(models.Model):
    title = models.CharField(max_length=255,unique=True)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20,choices=EVENT_STATUS_CHOICES,default="planned")
    registration_deadline = models.DateTimeField()
    event_type = models.CharField(max_length=255)
    reminder_time = models.DateTimeField()
    # forign key reletion
    venue = models.ForeignKey(Venue, on_delete=models.RESTRICT,null=True, blank=True)
    organizer = models.ForeignKey(Member, on_delete=models.RESTRICT,null=True, blank=True)
    media = models.ForeignKey(EventMedia, on_delete=models.RESTRICT,null=True, blank=True)
    # record keeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)      

    def __str__(self):
        return self.title


class EventTicket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.RESTRICT)
    ticket_name = models.CharField(max_length=255,unique=True)
    ticket_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    start_sale_date = models.DateTimeField()
    end_sale_date = models.DateTimeField()
    status = models.CharField(max_length=20,choices=EVENT_TICKET_STATUS_CHOICES,default="available")
    # record keeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    

    def __str__(self):
        return self.ticket_name
    
    
class EventFee(models.Model):
    event = models.ForeignKey(Event, on_delete=models.RESTRICT)
    membership_type = models.ForeignKey(MembershipType, on_delete=models.RESTRICT)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    # record keeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'membership_type')
    def __str__(self):
        return self.fee