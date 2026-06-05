from django.db import models
from users_management_app.models import User

class PropertyType(models.Model):
    """
    Property Type Choices
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'property_types'
        verbose_name_plural = 'Property Types'
    
    def __str__(self):
        return self.name


class Property(models.Model):
    """
    Property/Listing Model
    Represents properties available for rent or sale
    """
    
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),
    )
    
    LISTING_TYPE_CHOICES = (
        ('rent', 'For Rent'),
        ('sale', 'For Sale'),
        ('both', 'For Rent & Sale'),
    )
    
    # Landlord & Basic Info
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True)
    
    # Property Details
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES)
    number_of_rooms = models.IntegerField()
    number_of_bathrooms = models.IntegerField()
    square_meters = models.FloatField(null=True, blank=True)
    year_built = models.IntegerField(null=True, blank=True)
    
    # Amenities
    has_kitchen = models.BooleanField(default=True)
    has_water = models.BooleanField(default=True)
    has_electricity = models.BooleanField(default=True)
    furnished = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_garden = models.BooleanField(default=False)
    has_balcony = models.BooleanField(default=False)
    allows_pets = models.BooleanField(default=False)
    
    # Pricing
    rent_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    deposit_required = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    service_charges = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0)
    
    # Location
    country = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    cell = models.CharField(max_length=100)
    village = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Availability
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    available_from = models.DateField()
    lease_term_months = models.IntegerField(null=True, blank=True)
    
    # Security
    security_provider = models.CharField(max_length=255, null=True, blank=True)
    boundary_wall = models.BooleanField(default=False)
    
    # Contact Preference
    contact_method = models.CharField(
        max_length=50,
        choices=(
            ('direct', 'Direct Contact'),
            ('platform', 'Platform Only'),
            ('both', 'Both'),
        ),
        default='both'
    )
    
    # Statistics
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_views = models.IntegerField(default=0)
    total_applications = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'properties'
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.village}"


class PropertyImage(models.Model):
    """
    Property Images/Photos
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    caption = models.CharField(max_length=255, blank=True)
    is_main_image = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'property_images'
        verbose_name_plural = 'Property Images'
    
    def __str__(self):
        return f"Image for {self.property.title}"


class PropertyAmenity(models.Model):
    """
    Custom Amenities for properties
    """
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'property_amenities'
        verbose_name_plural = 'Property Amenities'
    
    def __str__(self):
        return self.name


class PropertyAmenityLink(models.Model):
    """
    Many-to-many relationship for Property and Amenities
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='amenities')
    amenity = models.ForeignKey(PropertyAmenity, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'property_amenity_links'
        unique_together = ('property', 'amenity')
    
    def __str__(self):
        return f"{self.property.title} - {self.amenity.name}"


class SavedProperty(models.Model):
    """
    Saved/Favorite properties by tenants
    """
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_properties')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_properties'
        unique_together = ('tenant', 'property')
    
    def __str__(self):
        return f"{self.tenant.email} saved {self.property.title}"
