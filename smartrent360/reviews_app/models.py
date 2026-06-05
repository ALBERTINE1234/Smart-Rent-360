from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from  users_management_app.models import User
from properties_app.models import Property
from bookings_app.models import Booking


class Review(models.Model):
    """
    Review/Rating model for properties and users
    """
    
    SUBJECT_CHOICES = (
        ('property', 'Property'),
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    )
    
    # Review Details
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    
    # Targets
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    reviewed_landlord = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='landlord_reviews')
    reviewed_tenant = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tenant_reviews')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    
    # Rating and Comments
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=255)
    comment = models.TextField()
    
    # Aspects Rating (for properties)
    cleanliness_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    location_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    value_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    safety_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Response from Reviewed User
    response = models.TextField(blank=True)
    response_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_verified_booking = models.BooleanField(default=False)
    
    # Images
    image1 = models.ImageField(upload_to='review_images/', null=True, blank=True)
    image2 = models.ImageField(upload_to='review_images/', null=True, blank=True)
    image3 = models.ImageField(upload_to='review_images/', null=True, blank=True)
    
    # Engagement
    helpful_count = models.IntegerField(default=0)
    unhelpful_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.reviewer.email} - {self.rating}/5"


class ReviewReply(models.Model):
    """
    Reply to review (owner response)
    """
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='owner_reply')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_replies')
    reply_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_replies'
    
    def __str__(self):
        return f"Reply to Review #{self.review.id}"


class ReviewImage(models.Model):
    """
    Additional images for reviews
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='review_images/')
    caption = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'review_images'
    
    def __str__(self):
        return f"Image for Review #{self.review.id}"


class ReviewHelpful(models.Model):
    """
    Track if users found review helpful
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField()
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_helpful'
        unique_together = ('review', 'user')
    
    def __str__(self):
        return f"{'Helpful' if self.is_helpful else 'Unhelpful'} vote on Review #{self.review.id}"


class MaintenanceRequest(models.Model):
    """
    Maintenance request from tenant to landlord
    """
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    )
    
    # Relationships
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_requests')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='maintenance_requests')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='maintenance_requests')
    
    # Request Details
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Images
    image1 = models.ImageField(upload_to='maintenance_requests/', null=True, blank=True)
    image2 = models.ImageField(upload_to='maintenance_requests/', null=True, blank=True)
    
    # Assigned To
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_maintenance'
    )
    
    # Completion
    completion_notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'maintenance_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Maintenance: {self.title}"
