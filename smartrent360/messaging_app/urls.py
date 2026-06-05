from django.urls import path
from .views import (
    MessageViewSet, ConversationViewSet,
    NotificationViewSet, AnnouncementViewSet
)

urlpatterns = [
    # Message endpoints
    path('', MessageViewSet.as_view({'get': 'list', 'post': 'create'}), name='message-list'),
    path('<int:pk>/', MessageViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='message-detail'),
    
    # Conversation endpoints
    path('conversations/', ConversationViewSet.as_view({'get': 'list', 'post': 'create'}), name='conversation-list'),
    path('conversations/<int:pk>/', ConversationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='conversation-detail'),
    
    # Notification endpoints
    path('notifications/', NotificationViewSet.as_view({'get': 'list', 'post': 'create'}), name='notification-list'),
    path('notifications/<int:pk>/', NotificationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='notification-detail'),
    
    # Announcement endpoints
    path('announcements/', AnnouncementViewSet.as_view({'get': 'list', 'post': 'create'}), name='announcement-list'),
    path('announcements/<int:pk>/', AnnouncementViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='announcement-detail'),
]
