from rest_framework import serializers
from .models import Payment, Receipt, Invoice, RentPaymentSchedule, PlatformCommission


class PaymentSerializer(serializers.ModelSerializer):
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'tenant', 'booking', 'property', 'payment_type',
            'amount', 'currency', 'status', 'payment_method',
            'transaction_id', 'reference_number', 'due_date',
            'payment_date', 'notes', 'is_overdue', 'created_at'
        ]
        read_only_fields = ['id', 'tenant', 'reference_number', 'created_at']
    
    def get_is_overdue(self, obj):
        return obj.is_overdue


class ReceiptSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = Receipt
        fields = [
            'id', 'payment', 'receipt_number', 'issued_by',
            'property_title', 'tenant_name', 'landlord_name',
            'period_from', 'period_to', 'receipt_file', 'issued_at'
        ]
        read_only_fields = ['id', 'receipt_number', 'issued_at']


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'id', 'booking', 'property', 'invoice_number', 'status',
            'billing_period_start', 'billing_period_end', 'rent_amount',
            'service_charges', 'other_charges', 'total_amount',
            'discount_amount', 'final_amount', 'due_date',
            'payment_received', 'payment_date', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'total_amount', 'created_at']


class RentPaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentPaymentSchedule
        fields = [
            'id', 'booking', 'payment_day_of_month', 'payment_method',
            'payment_account_number', 'payment_account_name',
            'is_active', 'auto_debit_enabled', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PlatformCommissionSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = PlatformCommission
        fields = [
            'id', 'payment', 'commission_type', 'commission_rate',
            'commission_amount', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
