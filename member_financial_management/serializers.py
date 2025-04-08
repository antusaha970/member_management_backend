from rest_framework import serializers
from .models import Invoice, PaymentMethod, IncomeParticular, IncomeReceivingOption


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


class IncomeParticularSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeParticular
        fields = "__all__"


class IncomeReceivingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeReceivingOption
        fields = "__all__"
