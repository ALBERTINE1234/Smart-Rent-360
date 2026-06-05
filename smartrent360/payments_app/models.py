from django.db import models
from django.utils import timezone
from  users_management_app.models import User
from properties_app.models import Property
from bookings_app.models import Booking


class Payment(models.Model):
    """
    Payment model for rent and other charges
    """
    
    PAYMENT_TYPE_CHOICES = (
        ('rent', 'Rent'),
        ('deposit', 'Deposit'),
        ('service_charge', 'Service Charge'),
        ('utilities', 'Utilities'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('cash', 'Cash'),
        ('check', 'Check'),
    )
    
    # Relationships
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    # property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='payments')
    rental_property = models.ForeignKey(Property, on_delete=models.CASCADE)
    # Payment Details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10, default='RWF')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    reference_number = models.CharField(max_length=255, unique=True)
    
    # Dates
    due_date = models.DateField()
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.tenant.email} - {self.amount} {self.currency}"
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        if self.status == 'completed':
            return False
        return self.due_date < timezone.now().date()


class Receipt(models.Model):
    """
    Payment receipt model
    """
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=255, unique=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_receipts')
    
    # Receipt Details
    property_title = models.CharField(max_length=255)
    tenant_name = models.CharField(max_length=255)
    landlord_name = models.CharField(max_length=255)
    
    period_from = models.DateField()
    period_to = models.DateField()
    
    # File
    receipt_file = models.FileField(upload_to='receipts/', null=True, blank=True)
    
    # Timestamps
    issued_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'receipts'
    
    def __str__(self):
        return f"Receipt #{self.receipt_number}"


class Invoice(models.Model):
    """
    Invoice model for tracking rental invoices
    """
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )
    
    # Relationships
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='invoices')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='invoices')
    
    # Invoice Details
    invoice_number = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Billing Period
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    
    # Amounts
    rent_amount = models.DecimalField(max_digits=15, decimal_places=2)
    service_charges = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Discounts and Adjustments
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Payment
    due_date = models.DateField()
    payment_received = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-billing_period_start']
    
    def __str__(self):
        return f"Invoice #{self.invoice_number}"


class RentPaymentSchedule(models.Model):
    """
    Automatic rent payment schedule
    """
    
    # Relationships
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment_schedule')
    
    # Schedule Details
    payment_day_of_month = models.IntegerField(default=1)  # 1-31
    payment_method = models.CharField(max_length=50, choices=Payment.PAYMENT_METHOD_CHOICES)
    
    # Account Details
    payment_account_number = models.CharField(max_length=255, null=True, blank=True)
    payment_account_name = models.CharField(max_length=255, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    auto_debit_enabled = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rent_payment_schedules'
    
    def __str__(self):
        return f"Schedule for {self.booking}"


class PlatformCommission(models.Model):
    """
    Track platform commission from landlords
    """
    
    COMMISSION_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('collected', 'Collected'),
        ('paid', 'Paid'),
    )
    
    # Relationships
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='platform_commission')
    
    # Commission Details
    commission_type = models.CharField(max_length=20, choices=COMMISSION_TYPE_CHOICES)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    commission_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'platform_commissions'
    
    def __str__(self):
        return f"Commission: {self.commission_amount}"
