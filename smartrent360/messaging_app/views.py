from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.utils import timezone

from .models import Message, Conversation, Notification, Announcement
from .serializers import (
    MessageSerializer, ConversationSerializer,
    NotificationSerializer, AnnouncementSerializer
)
from core.utils import APIResponse
from core.base_viewsets import BaseViewSet


class MessageViewSet(BaseViewSet):
    """
    Message ViewSet for direct messaging
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get messages for current user"""
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        )

    def perform_create(self, serializer):
        """Create a new message"""
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def send_message(self, request):
        """Send a message to another user"""
        try:
            recipient_id = request.data.get('recipient_id')
            message_text = request.data.get('message', '').strip()
            property_id = request.data.get('property_id')
            
            if not recipient_id:
                return APIResponse.bad_request("recipient_id is required")
            if not message_text:
                return APIResponse.bad_request("Message text is required")
            
            from users_management_app.models import User
            try:
                recipient = User.objects.get(id=recipient_id)
            except User.DoesNotExist:
                return APIResponse.not_found("Recipient not found")
            
            if recipient_id == request.user.id:
                return APIResponse.bad_request("You cannot send messages to yourself")
            
            message = Message.objects.create(
                sender=request.user,
                recipient=recipient,
                message=message_text,
                property_id=property_id if property_id else None
            )
            
            Conversation.objects.update_or_create(
                participant1=min(request.user, recipient, key=lambda x: x.id),
                participant2=max(request.user, recipient, key=lambda x: x.id),
                defaults={
                    'last_message': message_text,
                    'last_message_at': timezone.now(),
                }
            )
            
            return APIResponse.created(
                data=MessageSerializer(message).data,
                message="Message sent successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error sending message: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        """Mark message as read"""
        try:
            message = self.get_object()
            if request.user != message.recipient:
                return APIResponse.forbidden("You can only mark your own messages as read")
            
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
            
            return APIResponse.success(
                data=MessageSerializer(message).data,
                message="Message marked as read"
            )
        except Exception as e:
            return APIResponse.error(f"Error marking message as read: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def conversation_with(self, request):
        """Get conversation with a specific user"""
        try:
            other_user_id = request.query_params.get('user_id')
            if not other_user_id:
                return APIResponse.bad_request("user_id query parameter is required")
            
            from users_management_app.models import User
            try:
                other_user = User.objects.get(id=other_user_id)
            except User.DoesNotExist:
                return APIResponse.not_found("User not found")
            
            messages = Message.objects.filter(
                Q(sender=request.user, recipient=other_user) |
                Q(sender=other_user, recipient=request.user)
            ).order_by('created_at')
            
            serializer = MessageSerializer(messages, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=messages.count(),
                message="Conversation retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving conversation: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def unread_count(self, request):
        """Get count of unread messages"""
        try:
            unread = Message.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
            
            return APIResponse.success(
                data={'unread_count': unread},
                message="Unread message count retrieved"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving unread count: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationViewSet(BaseViewSet):
    """
    Conversation ViewSet
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get conversations for current user"""
        user = self.request.user
        return Conversation.objects.filter(
            Q(participant1=user) | Q(participant2=user)
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_conversations(self, request):
        """Get all conversations for current user"""
        try:
            conversations = Conversation.objects.filter(
                Q(participant1=request.user) | Q(participant2=request.user)
            )
            serializer = ConversationSerializer(conversations, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=conversations.count(),
                message="Conversations retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving conversations: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    Notification ViewSet
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get notifications for current user"""
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def unread(self, request):
        """Get unread notifications"""
        try:
            notifications = Notification.objects.filter(
                recipient=request.user,
                is_read=False
            )
            serializer = NotificationSerializer(notifications, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=notifications.count(),
                message="Unread notifications retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving notifications: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        try:
            notification = self.get_object()
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            
            return APIResponse.success(
                data=NotificationSerializer(notification).data,
                message="Notification marked as read"
            )
        except Exception as e:
            return APIResponse.error(f"Error marking notification as read: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_all_as_read(self, request):
        """Mark all notifications as read"""
        try:
            Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).update(
                is_read=True,
                read_at=timezone.now()
            )
            
            return APIResponse.success(
                message="All notifications marked as read"
            )
        except Exception as e:
            return APIResponse.error(f"Error marking notifications as read: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def clear_all(self, request):
        """Clear all notifications"""
        try:
            count = Notification.objects.filter(recipient=request.user).count()
            Notification.objects.filter(recipient=request.user).delete()
            return APIResponse.success(
                message=f"{count} notifications cleared successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error clearing notifications: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnnouncementViewSet(BaseViewSet):
    """
    Announcement ViewSet - Read only for users
    """
    serializer_class = AnnouncementSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Get published announcements"""
        queryset = Announcement.objects.filter(
            is_published=True,
            published_at__isnull=False
        )
        
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'tenant':
                queryset = queryset.filter(
                    Q(audience='all') | Q(audience='tenants')
                )
            elif user.role == 'landlord':
                queryset = queryset.filter(
                    Q(audience='all') | Q(audience='landlords')
                )
            elif user.role == 'admin':
                queryset = queryset.filter(
                    Q(audience='all') | Q(audience='admins')
                )
        else:
            queryset = queryset.filter(audience='all')
        
        return queryset.order_by('-published_at')
