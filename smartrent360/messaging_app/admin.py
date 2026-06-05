from django.contrib import admin
from .models import Message, Conversation, Notification, Announcement

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__email', 'recipient__email')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('participant1', 'participant2', 'last_message_at')
    list_filter = ('last_message_at',)
    search_fields = ('participant1__email', 'participant2__email')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__email', 'title')
    readonly_fields = ('created_at',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'audience', 'is_published', 'created_at')
    list_filter = ('audience', 'is_published', 'priority')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
