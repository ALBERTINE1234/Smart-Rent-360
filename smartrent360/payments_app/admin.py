from django.contrib import admin
from .models import Payment, Receipt, Invoice, RentPaymentSchedule, PlatformCommission

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'amount', 'status', 'due_date')
    list_filter = ('status', 'payment_type', 'due_date')
    search_fields = ('tenant__email', 'reference_number')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'tenant_name', 'issued_at')
    list_filter = ('issued_at',)
    search_fields = ('receipt_number', 'tenant_name')
    readonly_fields = ('issued_at',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'booking', 'status', 'due_date')
    list_filter = ('status', 'due_date')
    search_fields = ('invoice_number',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(RentPaymentSchedule)
class RentPaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ('booking', 'payment_method', 'is_active')
    list_filter = ('is_active', 'payment_method')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PlatformCommission)
class PlatformCommissionAdmin(admin.ModelAdmin):
    list_display = ('commission_amount', 'status', 'created_at')
    list_filter = ('status', 'commission_type')
    readonly_fields = ('created_at', 'updated_at')
