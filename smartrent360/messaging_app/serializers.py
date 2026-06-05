from rest_framework import serializers
from .models import Message, Conversation, Notification, Announcement
from  users_management_app.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'recipient', 'property', 'message',
            'file_attachment', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'sender', 'read_at', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    participant1 = UserSerializer(read_only=True)
    participant2 = UserSerializer(read_only=True)
    latest_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participant1', 'participant2', 'property',
            'last_message', 'last_message_at', 'unread_count_p1',
            'unread_count_p2', 'is_active', 'latest_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'participant1', 'participant2', 'created_at', 'updated_at']
    
    def get_latest_message(self, obj):
        latest = Message.objects.filter(
            models.Q(sender=obj.participant1, recipient=obj.participant2) |
            models.Q(sender=obj.participant2, recipient=obj.participant1)
        ).first()
        if latest:
            return MessageSerializer(latest).data
        return None


class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'notification_type', 'title', 'message',
            'related_id', 'is_read', 'read_at', 'via_email', 'via_sms',
            'via_app', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'recipient', 'read_at', 'created_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'image', 'audience', 'priority',
            'is_published', 'published_at', 'expires_at', 'author',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
