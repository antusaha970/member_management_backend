from rest_framework import serializers
from .models import Invoice, PaymentMethod, IncomeParticular, IncomeReceivingOption, InvoiceItem, Income, Sale, Transaction, Payment, Due, MemberDue
from restaurant.models import Restaurant
from event.models import Event, EventTicket
from product.models import Product
from facility.models import Facility
import pdb


class InvoiceSerializer(serializers.ModelSerializer):
    invoice_type = serializers.CharField()
    generated_by = serializers.CharField()
    member = serializers.CharField()
    restaurant = serializers.CharField()

    class Meta:
        model = Invoice
        fields = "__all__"


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


class InvoicePaymentSerializer(serializers.Serializer):
    invoice_id = serializers.PrimaryKeyRelatedField(
        queryset=Invoice.objects.all())
    payment_method = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.all())
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    income_particular = serializers.PrimaryKeyRelatedField(
        queryset=IncomeParticular.objects.all())
    received_from = serializers.PrimaryKeyRelatedField(
        queryset=IncomeReceivingOption.objects.all())

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Please pass a valid amount")
        return value

    def validate(self, attrs):
        invoice = attrs["invoice_id"]
        if invoice.is_full_paid:
            raise serializers.ValidationError(
                "This invoice is already fully paid")
        return attrs


class IncomeParticularSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeParticular
        fields = "__all__"


class IncomeReceivingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeReceivingOption
        fields = "__all__"


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "name"]  # Add other fields as needed


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name"]


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ["id", "name"]


class EventTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTicket
        fields = ["id", "ticket_name"]


class InvoiceItemSerializer(serializers.ModelSerializer):
    restaurant_items = RestaurantSerializer(many=True)
    products = ProductSerializer(many=True)
    facility = FacilitySerializer(many=True)
    event_tickets = EventTicketSerializer(many=True)

    class Meta:
        model = InvoiceItem
        fields = [
            "id",
            "restaurant_items",
            "products",
            "facility",
            "event_tickets",
        ]


class InvoiceForViewSerializer(serializers.ModelSerializer):
    invoice_type = serializers.StringRelatedField()
    generated_by = serializers.StringRelatedField()
    member = serializers.StringRelatedField()
    restaurant = serializers.StringRelatedField()
    event = serializers.StringRelatedField()
    invoice_items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = "__all__"


class IncomeSerializer(serializers.ModelSerializer):
    particular = serializers.StringRelatedField()
    received_from_type = serializers.StringRelatedField()
    receiving_type = serializers.StringRelatedField()
    member = serializers.SerializerMethodField()
    received_by = serializers.StringRelatedField()
    sale = serializers.StringRelatedField()

    class Meta:
        model = Income
        fields = "__all__"

    def get_member(self, obj):
        return obj.member.member_ID


class SaleSerializer(serializers.ModelSerializer):
    sale_source_type = serializers.StringRelatedField()
    customer = serializers.SerializerMethodField()
    payment_method = serializers.StringRelatedField()
    invoice = serializers.StringRelatedField()

    class Meta:
        model = Sale
        fields = "__all__"

    def get_customer(self, obj):
        return obj.customer.member_ID


class IncomeSpecificSerializer(serializers.ModelSerializer):
    particular = serializers.StringRelatedField()
    received_from_type = serializers.StringRelatedField()
    receiving_type = serializers.StringRelatedField()
    member = serializers.SerializerMethodField()
    received_by = serializers.StringRelatedField()
    sale = SaleSerializer()

    class Meta:
        model = Income
        fields = "__all__"

    def get_member(self, obj):
        return obj.member.member_ID


class SaleSpecificSerializer(serializers.ModelSerializer):
    sale_source_type = serializers.StringRelatedField()
    customer = serializers.SerializerMethodField()
    payment_method = serializers.StringRelatedField()
    invoice = InvoiceForViewSerializer()

    class Meta:
        model = Sale
        fields = "__all__"

    def get_customer(self, obj):
        return obj.customer.member_ID


class TransactionSerializer(serializers.ModelSerializer):
    invoice = serializers.StringRelatedField()
    payment_method = serializers.StringRelatedField()
    member = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = "__all__"

    def get_member(self, obj):
        return obj.member.member_ID


class TransactionSpecificSerializer(serializers.ModelSerializer):
    invoice = InvoiceForViewSerializer()
    payment_method = serializers.StringRelatedField()
    member = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = "__all__"

    def get_member(self, obj):
        return obj.member.member_ID


class PaymentSerializer(serializers.ModelSerializer):
    invoice = serializers.StringRelatedField()
    member = serializers.SerializerMethodField()
    payment_method = serializers.StringRelatedField()
    processed_by = serializers.SerializerMethodField()
    transaction = serializers.StringRelatedField()

    class Meta:
        model = Payment
        fields = "__all__"

    def get_member(self, obj):
        return obj.member.member_ID

    def get_processed_by(self, obj):
        return obj.processed_by.username


class PaymentSpecificSerializer(serializers.ModelSerializer):
    invoice = InvoiceSerializer()
    member = serializers.SerializerMethodField()
    payment_method = serializers.StringRelatedField()
    processed_by = serializers.SerializerMethodField()
    transaction = TransactionSerializer()

    class Meta:
        model = Payment
        fields = "__all__"

    def get_member(self, obj):
        return obj.member.member_ID

    def get_processed_by(self, obj):
        return obj.processed_by.username


class DuesSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()
    invoice = serializers.StringRelatedField()
    payment = serializers.SerializerMethodField()
    transaction = serializers.StringRelatedField()

    class Meta:
        model = Due
        fields = "__all__"

    def get_member(self, obj):
        return obj.member.member_ID

    def get_payment(self, obj):
        return obj.payment.id


class DuesSpecificSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()
    invoice = InvoiceSerializer()
    payment = PaymentSerializer()
    transaction = TransactionSerializer()

    class Meta:
        model = Due
        fields = "__all__"

    def get_member(self, obj):
        return obj.member.member_ID

    def get_payment(self, obj):
        return obj.payment.id


class MemberDueSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()

    class Meta:
        model = MemberDue
        fields = "__all__"

    def get_member(self, obj):
        return obj.member.member_ID


class MemberDueSpecificSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()
    due_reference = DuesSerializer()

    class Meta:
        model = MemberDue
        fields = "__all__"

    def get_member(self, obj):
        return obj.member.member_ID
