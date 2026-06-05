from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    """
    Custom User Model with role-based access control
    Roles: tenant, landlord, commissioner, government, admin
    """
    
    ROLE_CHOICES = (
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
        ('commissioner', 'Commissioner'),
        ('government', 'Government'),
        ('admin', 'Admin'),
    )

    # Core Fields
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')
    
    # Verification & Security
    is_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    
    # Profile Information
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    national_id = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Address Fields
    country = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    cell = models.CharField(max_length=100, null=True, blank=True)
    village = models.CharField(max_length=100, null=True, blank=True)
    email_verification_token = models.CharField(max_length=64, unique=True, null=True, blank=True, default=None)
    password_reset_token = models.CharField(max_length=64, unique=True, null=True, blank=True, default=None)
    # Language Preference
    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('rw', 'Kinyarwanda'),
        ('fr', 'French'),
        ('sw', 'Kiswahili'),
    )
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    
    # Communication Preference
    receive_notifications = models.BooleanField(default=True)
    receive_email_notifications = models.BooleanField(default=True)
    receive_sms_notifications = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"


class LandlordProfile(models.Model):
    """
    Extended profile for Landlord users
    Contains landlord-specific information
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlord_profile')
    business_name = models.CharField(max_length=255, null=True, blank=True)
    business_registration = models.CharField(max_length=255, null=True, blank=True)
    tax_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Banking & Payment
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    mobile_money_provider = models.CharField(max_length=100, null=True, blank=True)
    mobile_money_number = models.CharField(max_length=20, null=True, blank=True)
    
    # Verification Status
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=(('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')),
        default='pending'
    )
    
    # Statistics
    total_properties = models.IntegerField(default=0)
    total_tenants = models.IntegerField(default=0)
    monthly_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'landlord_profiles'
        verbose_name = 'Landlord Profile'
        verbose_name_plural = 'Landlord Profiles'

    def __str__(self):
        return f"Landlord Profile - {self.user.email}"


class TenantProfile(models.Model):
    """
    Extended profile for Tenant users
    Contains tenant-specific information
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')
    
    # Employment Information
    employment_status = models.CharField(
        max_length=50,
        choices=(
            ('employed', 'Employed'),
            ('self_employed', 'Self Employed'),
            ('student', 'Student'),
            ('unemployed', 'Unemployed'),
            ('retired', 'Retired'),
        ),
        null=True,
        blank=True
    )
    employer_name = models.CharField(max_length=255, null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    
    # Financial Information
    monthly_income = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    budget_min = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # References
    reference_name = models.CharField(max_length=255, null=True, blank=True)
    reference_phone = models.CharField(max_length=20, null=True, blank=True)
    reference_email = models.EmailField(null=True, blank=True)
    
    # Rental History
    previous_landlord_name = models.CharField(max_length=255, null=True, blank=True)
    previous_landlord_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Verification Status
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=(('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')),
        default='pending'
    )
    
    # Preferences
    preferred_property_type = models.CharField(max_length=100, null=True, blank=True)
    move_in_date = models.DateField(null=True, blank=True)
    lease_length_preference = models.CharField(max_length=50, null=True, blank=True)
    
    # Statistics
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_rentals = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tenant_profiles'
        verbose_name = 'Tenant Profile'
        verbose_name_plural = 'Tenant Profiles'

    def __str__(self):
        return f"Tenant Profile - {self.user.email}"