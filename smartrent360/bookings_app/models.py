from django.db import models
from  users_management_app.models import User
from properties_app.models import Property


class Booking(models.Model):
    """
    Booking/Application model
    Represents tenant applications for properties
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('active', 'Active Lease'),
        ('completed', 'Completed'),
    )
    
    # Relationships
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    
    # Application Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Tenant's application message")
    
    # Lease Details
    move_in_date = models.DateField()
    lease_term_months = models.IntegerField()
    expected_move_out_date = models.DateField(null=True, blank=True)
    
    # Occupancy
    number_of_occupants = models.IntegerField(default=1)
    
    # Landlord Actions
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bookings')
    approval_date = models.DateTimeField(null=True, blank=True)
    approval_message = models.TextField(blank=True)
    
    # Rejection Details
    rejection_reason = models.TextField(blank=True)
    rejected_date = models.DateTimeField(null=True, blank=True)
    
    # Dates
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-applied_at']
        unique_together = ('tenant', 'property')
    
    def __str__(self):
        return f"{self.tenant.email} - {self.property.title}"


class PropertyVisit(models.Model):
    """
    Scheduled property visits/viewings
    """
    
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Relationships
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_visits')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='visits')
    
    # Visit Details
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    
    # Landlord Response
    confirmed_by_landlord = models.BooleanField(default=False)
    landlord_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'property_visits'
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"Visit: {self.tenant.email} - {self.property.title}"


class LeaseAgreement(models.Model):
    """
    Digital Lease Agreement
    """
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_signature', 'Pending Signature'),
        ('signed', 'Signed'),
        ('terminated', 'Terminated'),
    )
    
    # Relationships
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='lease_agreement')
    
    # Agreement Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    contract_number = models.CharField(max_length=100, unique=True)
    
    # Terms
    monthly_rent = models.DecimalField(max_digits=15, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Terms and Conditions
    terms = models.TextField()
    special_conditions = models.TextField(blank=True)
    
    # Document
    document_file = models.FileField(upload_to='lease_agreements/', null=True, blank=True)
    
    # Signatures
    landlord_signed = models.BooleanField(default=False)
    landlord_signature_date = models.DateTimeField(null=True, blank=True)
    tenant_signed = models.BooleanField(default=False)
    tenant_signature_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lease_agreements'
    
    def __str__(self):
        return f"Lease: {self.contract_number}"
