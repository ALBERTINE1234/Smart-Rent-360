from django.contrib import admin
from .models import Property, PropertyType, PropertyImage, PropertyAmenity, SavedProperty

@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'landlord', 'status', 'rent_price', 'created_at')
    list_filter = ('status', 'listing_type', 'district')
    search_fields = ('title', 'village')
    readonly_fields = ('total_views', 'total_applications', 'rating')

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'is_main_image')
    list_filter = ('is_main_image',)

@admin.register(PropertyAmenity)
class PropertyAmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'property', 'saved_at')
    list_filter = ('saved_at',)
