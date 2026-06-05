from django.contrib import admin
from .models import Review, ReviewReply, ReviewImage, ReviewHelpful, MaintenanceRequest

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'subject', 'rating', 'status', 'created_at')
    list_filter = ('subject', 'status', 'rating', 'created_at')
    search_fields = ('reviewer__email', 'title')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ('review', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author__email',)
    readonly_fields = ('created_at',)

@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ('review', 'caption')
    search_fields = ('caption',)

@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'is_helpful', 'voted_at')
    list_filter = ('is_helpful', 'voted_at')
    search_fields = ('user__email',)

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'tenant', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('tenant__email', 'title')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
