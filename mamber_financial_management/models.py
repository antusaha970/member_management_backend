from django.db import models
from django.contrib.auth import get_user_model
from member.models import Member
from restaurant.models import Restaurant

User = get_user_model()


class FinancialBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class InvoiceType(FinancialBaseModel):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Invoice(FinancialBaseModel):
    INVOICE_STATUS_CHOICES = [
        ('paid', 'paid'),
        ('unpaid', 'unpaid'),
        ('partial_paid', 'partial_paid'),
        ('due', 'due'),
    ]
    currency = models.CharField(max_length=20, blank=True, default="")
    invoice_number = models.CharField(max_length=100, unique=True)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(blank=True, null=True, default=None)
    issue_date = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_full_paid = models.BooleanField()
    status = models.CharField(max_length=30, choices=INVOICE_STATUS_CHOICES)

    # relations
    invoice_type = models.ForeignKey(
        InvoiceType, on_delete=models.PROTECT, related_name="invoice_type")
    generated_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="generated_by", blank=True, null=True)
    member = models.ForeignKey(
        Member, on_delete=models.PROTECT, related_name="invoice_member", blank=True, null=True)
    # invoice of
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT,
                                   related_name="restaurant_invoice", blank=True, null=True, default=None)
    # event = models.ForeignKey(Event, on_delete=models.PROTECT,
    #                                related_name="restaurant_invoice", blank=True, null=True, default=None)

    def __str__(self):
        return f"${self.invoice_number}"


class InvoiceItem(FinancialBaseModel):
    # relations
    invoice = models.ForeignKey(
        Invoice, on_delete=models.PROTECT, related_name="invoice_items")
    restaurant_items = models.ManyToManyField()
