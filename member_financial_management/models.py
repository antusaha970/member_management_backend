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
    status = models.CharField(
        max_length=30, choices=INVOICE_STATUS_CHOICES, default="unpaid")

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
    restaurant_items = models.ManyToManyField(
        Restaurant, related_name="restaurant_items")
    # TODO: add event,product,facility

    def __str__(self):
        return f"${self.invoice.invoice_number}"


class PaymentMethod(FinancialBaseModel):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Transaction(FinancialBaseModel):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=300, blank=True, default="")
    transaction_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=100, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    adjustment_reason = models.TextField(blank=True, default="")

    # relations
    member = models.ForeignKey(
        Member, on_delete=models.PROTECT, related_name="transaction_member")
    invoice = models.ForeignKey(
        Invoice, on_delete=models.PROTECT, related_name="transaction_invoice")
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT, related_name="transaction_payment_method")

    def __str__(self):
        return self.amount


class Payment(FinancialBaseModel):
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'paid'),
        ('unpaid', 'unpaid'),
        ('partial_paid', 'partial_paid'),
        ('due', 'due'),
    ]
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=30, choices=PAYMENT_STATUS_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_gateway = models.CharField(max_length=100, blank=True, default="")
    notes = models.TextField()

    # relations
    invoice = models.ForeignKey(
        Invoice, on_delete=models.PROTECT, related_name="payment_invoice")
    member = models.ForeignKey(Member, on_delete=models.PROTECT,
                               related_name="payment_member", blank=True, null=True)
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT, related_name="payment_payment_method", blank=True, null=True)
    processed_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="payment_processed_by", blank=True, null=True)
    transaction = models.ForeignKey(
        Transaction, on_delete=models.PROTECT, related_name="payment_transaction")

    def __str__(self):
        return f"{self.invoice.invoice_number}"


class SaleType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Sale(FinancialBaseModel):
    sale_number = models.CharField(max_length=300, unique=True)
    sale_source_id = models.CharField(max_length=10, blank=True, null=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=150, blank=True, default="")
    sales_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True, default=None)
    notes = models.TextField(blank=True, default="")
    promo_code = models.CharField(max_length=300, blank=True, default="")

    # relation
    sale_source_type = models.ForeignKey(
        SaleType, on_delete=models.PROTECT, related_name="sale_source")
    customer = models.ForeignKey(
        Member, on_delete=models.PROTECT, related_name="sale_customer")
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT, related_name="payment_method")
    invoice = models.ForeignKey(
        Invoice, on_delete=models.PROTECT, related_name="sale_invoice")

    def __str__(self):
        return self.sale_number


class IncomeParticular(FinancialBaseModel):
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name


class IncomeReceivingOption(FinancialBaseModel):
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name


class IncomeReceivingType(FinancialBaseModel):
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name


class Income(FinancialBaseModel):
    date = models.DateTimeField(auto_now_add=True)
    receivable_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    discount_name = models.CharField(max_length=255, blank=True, default="")
    discounted_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    final_receivable = models.DecimalField(max_digits=10, decimal_places=2)
    actual_received = models.DecimalField(max_digits=10, decimal_places=2)
    reaming_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_payable_last_date = models.DateField(
        blank=True, null=True, default=None)

    # relations
    particular = models.ForeignKey(
        IncomeParticular, on_delete=models.PROTECT, related_name="income_particular")

    received_from_type = models.ForeignKey(
        IncomeReceivingOption, on_delete=models.PROTECT, related_name="income_received_from_type")

    receiving_type = models.ForeignKey(
        IncomeReceivingType, on_delete=models.PROTECT, related_name="income_receiving_type")

    member = models.ForeignKey(
        Member, on_delete=models.PROTECT, related_name="income_member")
    received_by = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT, related_name="income_received_by")
