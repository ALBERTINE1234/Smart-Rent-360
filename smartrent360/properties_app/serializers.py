from rest_framework import serializers
from .models import (
    Property, PropertyType, PropertyImage, PropertyAmenity, 
    PropertyAmenityLink, SavedProperty
)
from users_management_app.serializers import UserSerializer


class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyType
        fields = ['id', 'name', 'description']


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'caption', 'is_main_image', 'uploaded_at']


class PropertyAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyAmenity
        fields = ['id', 'name', 'icon']


class PropertySerializer(serializers.ModelSerializer):
    landlord = UserSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    amenities = PropertyAmenitySerializer(many=True, read_only=True, source='amenities.all')
    property_type = PropertyTypeSerializer(read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'landlord', 'title', 'description', 'property_type',
            'listing_type', 'number_of_rooms', 'number_of_bathrooms',
            'square_meters', 'year_built', 'has_kitchen', 'has_water',
            'has_electricity', 'furnished', 'has_parking', 'has_garden',
            'has_balcony', 'allows_pets', 'rent_price', 'sale_price',
            'deposit_required', 'service_charges', 'country', 'province',
            'district', 'sector', 'cell', 'village', 'street_address',
            'latitude', 'longitude', 'status', 'available_from',
            'lease_term_months', 'security_provider', 'boundary_wall',
            'contact_method', 'rating', 'total_views', 'total_applications',
            'images', 'amenities', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'landlord', 'total_views', 'total_applications', 'rating', 'created_at', 'updated_at']


class SavedPropertySerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    
    class Meta:
        model = SavedProperty
        fields = ['id', 'tenant', 'property', 'saved_at']
        read_only_fields = ['id', 'tenant', 'saved_at']
