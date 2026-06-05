from rest_framework import serializers
from .models import User, LandlordProfile, TenantProfile
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Basic User Serializer"""
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone_number', 'role', 'is_verified', 'profile_photo',
            'country', 'district', 'preferred_language', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'role']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {"message": "This email is already registered."}
            )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user

class LandlordProfileSerializer(serializers.ModelSerializer):
    """Landlord Profile Serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = LandlordProfile
        fields = [
            'id', 'user', 'business_name', 'business_registration',
            'tax_id', 'bank_name', 'account_number', 'mobile_money_provider',
            'mobile_money_number', 'is_verified', 'verification_status',
            'total_properties', 'total_tenants', 'monthly_income',
            'rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_properties', 'total_tenants', 'rating', 'created_at', 'updated_at']


class TenantProfileSerializer(serializers.ModelSerializer):
    """Tenant Profile Serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TenantProfile
        fields = [
            'id', 'user', 'employment_status', 'employer_name',
            'occupation', 'monthly_income', 'budget_min', 'budget_max',
            'reference_name', 'reference_phone', 'reference_email',
            'previous_landlord_name', 'previous_landlord_phone',
            'is_verified', 'verification_status', 'preferred_property_type',
            'move_in_date', 'lease_length_preference', 'rating',
            'total_rentals', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_rentals', 'rating', 'created_at', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    """User Registration Serializer"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password2', 'first_name',
            'last_name', 'phone_number', 'role', 'country', 'district'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number'),
            role=validated_data.get('role', 'tenant'),
            country=validated_data.get('country'),
            district=validated_data.get('district'),
        )
        
        # Create appropriate profile based on role
        if validated_data.get('role') == 'landlord':
            LandlordProfile.objects.create(user=user)
        elif validated_data.get('role') == 'tenant':
            TenantProfile.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    """User Login Serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Change Password Serializer"""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Passwords don't match."})
        return attrs