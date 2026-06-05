from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LandlordProfile, TenantProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_verified', 'is_active')
    list_filter = ('role', 'is_verified', 'is_active', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Info', {
            'fields': ('phone_number', 'role', 'profile_photo', 'national_id', 'date_of_birth')
        }),
        ('Verification', {
            'fields': ('is_verified', 'is_email_verified', 'is_phone_verified')
        }),
        ('Location', {
            'fields': ('country', 'province', 'district', 'sector', 'cell', 'village')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'receive_notifications', 'receive_email_notifications', 'receive_sms_notifications')
        }),
    )

@admin.register(LandlordProfile)
class LandlordProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'verification_status', 'total_properties', 'rating')
    list_filter = ('is_verified', 'verification_status')
    search_fields = ('user__email', 'business_name')
    readonly_fields = ('created_at', 'updated_at', 'total_properties', 'total_tenants', 'rating')

@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employment_status', 'is_verified', 'total_rentals', 'rating')
    list_filter = ('employment_status', 'is_verified')
    search_fields = ('user__email', 'employer_name')
    readonly_fields = ('created_at', 'updated_at', 'total_rentals', 'rating')

