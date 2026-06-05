from rest_framework import serializers
from .models import Review, ReviewReply, ReviewImage, ReviewHelpful, MaintenanceRequest
from  users_management_app.serializers import UserSerializer


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'caption']


class ReviewReplySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = ReviewReply
        fields = ['id', 'author', 'reply_text', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    reviewed_landlord = UserSerializer(read_only=True)
    reviewed_tenant = UserSerializer(read_only=True)
    owner_reply = ReviewReplySerializer(read_only=True)
    additional_images = ReviewImageSerializer(many=True, read_only=True)
    average_aspect_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'reviewer', 'subject', 'property', 'reviewed_landlord',
            'reviewed_tenant', 'booking', 'rating', 'title', 'comment',
            'cleanliness_rating', 'location_rating', 'value_rating',
            'safety_rating', 'average_aspect_rating', 'response',
            'response_date', 'status', 'is_verified_booking',
            'helpful_count', 'unhelpful_count', 'owner_reply',
            'additional_images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reviewer', 'response', 'response_date', 'status', 'created_at']
    
    def get_average_aspect_rating(self, obj):
        ratings = [obj.cleanliness_rating, obj.location_rating, obj.value_rating, obj.safety_rating]
        valid_ratings = [r for r in ratings if r is not None]
        if valid_ratings:
            return sum(valid_ratings) / len(valid_ratings)
        return None


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    tenant = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'tenant', 'property', 'booking', 'title', 'description',
            'priority', 'status', 'image1', 'image2', 'assigned_to',
            'completion_notes', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'completed_at', 'created_at', 'updated_at']
