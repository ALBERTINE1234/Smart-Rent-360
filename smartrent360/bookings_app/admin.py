from django.contrib import admin
from .models import Booking, PropertyVisit, LeaseAgreement

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'property', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('tenant__email', 'property__title')
    readonly_fields = ('applied_at', 'updated_at')

@admin.register(PropertyVisit)
class PropertyVisitAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'property', 'scheduled_date', 'status')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('tenant__email', 'property__title')

@admin.register(LeaseAgreement)
class LeaseAgreementAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'booking', 'status', 'start_date')
    list_filter = ('status', 'start_date')
    search_fields = ('contract_number', 'booking__tenant__email')
    readonly_fields = ('contract_number', 'created_at', 'updated_at')
