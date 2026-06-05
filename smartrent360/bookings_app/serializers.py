from rest_framework import serializers
from .models import Booking, PropertyVisit, LeaseAgreement
from  users_management_app.serializers import UserSerializer
from properties_app.serializers import PropertySerializer


class BookingSerializer(serializers.ModelSerializer):
    tenant = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'tenant', 'property', 'status', 'message',
            'move_in_date', 'lease_term_months', 'expected_move_out_date',
            'number_of_occupants', 'approved_by', 'approval_date',
            'approval_message', 'rejection_reason', 'rejected_date',
            'applied_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'approved_by', 'approval_date', 'rejected_date', 'applied_at', 'updated_at']


class PropertyVisitSerializer(serializers.ModelSerializer):
    tenant = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)
    
    class Meta:
        model = PropertyVisit
        fields = [
            'id', 'tenant', 'property', 'scheduled_date', 'status',
            'notes', 'confirmed_by_landlord', 'landlord_notes',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'tenant', 'created_at', 'completed_at']


class LeaseAgreementSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    
    class Meta:
        model = LeaseAgreement
        fields = [
            'id', 'booking', 'status', 'contract_number',
            'monthly_rent', 'deposit_amount', 'start_date', 'end_date',
            'terms', 'special_conditions', 'document_file',
            'landlord_signed', 'landlord_signature_date',
            'tenant_signed', 'tenant_signature_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'booking', 'contract_number', 'created_at', 'updated_at']
