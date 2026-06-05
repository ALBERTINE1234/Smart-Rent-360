from django.db import models
from  users_management_app.models import User
from properties_app.models import Property


class Message(models.Model):
    """
    Direct message between users
    """
    
    # Relationships
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    
    # Message Content
    message = models.TextField()
    file_attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'recipient']),
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        return f"{self.sender.email} to {self.recipient.email}"


class Conversation(models.Model):
    """
    Conversation thread between two users
    """
    
    # Participants
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_p2')
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    
    # Statistics
    unread_count_p1 = models.IntegerField(default=0)
    unread_count_p2 = models.IntegerField(default=0)
    
    # Last Message
    last_message = models.TextField(blank=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversations'
        unique_together = ('participant1', 'participant2')
        ordering = ['-last_message_at']
    
    def __str__(self):
        return f"Conversation: {self.participant1.email} & {self.participant2.email}"


class Notification(models.Model):
    """
    Notification system for users
    """
    
    NOTIFICATION_TYPE_CHOICES = (
        ('application', 'Application'),
        ('message', 'Message'),
        ('payment', 'Payment'),
        ('property_update', 'Property Update'),
        ('booking_status', 'Booking Status'),
        ('maintenance', 'Maintenance'),
        ('review', 'Review'),
        ('system', 'System'),
    )
    
    # Recipient
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    # Notification Details
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related Object
    related_id = models.IntegerField(null=True, blank=True)  # ID of related object (Booking, Payment, etc.)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Preferences
    via_email = models.BooleanField(default=True)
    via_sms = models.BooleanField(default=False)
    via_app = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} - {self.recipient.email}"


class Announcement(models.Model):
    """
    System announcements for all users or specific roles
    """
    
    AUDIENCE_CHOICES = (
        ('all', 'All Users'),
        ('tenants', 'Tenants'),
        ('landlords', 'Landlords'),
        ('admins', 'Admins'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    # Content
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='announcements/', null=True, blank=True)
    
    # Target
    audience = models.CharField(max_length=50, choices=AUDIENCE_CHOICES, default='all')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Status
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Author
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='announcements')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'announcements'
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title
