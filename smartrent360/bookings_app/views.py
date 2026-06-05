from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import Booking, PropertyVisit, LeaseAgreement
from .serializers import BookingSerializer, PropertyVisitSerializer, LeaseAgreementSerializer
from core.utils import APIResponse
from core.base_viewsets import BaseViewSet


class BookingViewSet(BaseViewSet):
    """
    Booking ViewSet for tenant applications
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter bookings based on user role"""
        user = self.request.user
        if user.role == 'tenant':
            return Booking.objects.filter(tenant=user)
        elif user.role == 'landlord':
            return Booking.objects.filter(property__landlord=user)
        elif user.role == 'admin':
            return Booking.objects.all()
        return Booking.objects.none()

    def perform_create(self, serializer):
        """Create booking - tenant only"""
        if self.request.user.role != 'tenant':
            raise PermissionError('Only tenants can create bookings')
        serializer.save(tenant=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def apply_for_property(self, request):
        """Tenant applies for a property"""
        try:
            if request.user.role != 'tenant':
                return APIResponse.forbidden("Only tenants can apply for properties")
            
            serializer = BookingSerializer(data=request.data)
            if serializer.is_valid():
                booking = serializer.save(tenant=request.user)
                booking.property.total_applications += 1
                booking.property.save(update_fields=['total_applications'])
                return APIResponse.created(
                    data=BookingSerializer(booking).data,
                    message="Application submitted successfully"
                )
            return APIResponse.validation_error("Booking validation failed", serializer.errors)
        except Exception as e:
            return APIResponse.error(f"Error applying for property: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """Landlord approves booking"""
        try:
            booking = self.get_object()
            if request.user != booking.property.landlord and request.user.role != 'admin':
                return APIResponse.forbidden("You don't have permission to approve this booking")
            
            booking.status = 'approved'
            booking.approved_by = request.user
            booking.approval_date = timezone.now()
            booking.approval_message = request.data.get('message', '')
            booking.save()
            
            return APIResponse.success(
                data=BookingSerializer(booking).data,
                message="Booking approved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error approving booking: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """Landlord rejects booking"""
        try:
            booking = self.get_object()
            if request.user != booking.property.landlord and request.user.role != 'admin':
                return APIResponse.forbidden("You don't have permission to reject this booking")
            
            booking.status = 'rejected'
            booking.rejected_date = timezone.now()
            booking.rejection_reason = request.data.get('reason', '')
            booking.save()
            
            return APIResponse.success(
                data=BookingSerializer(booking).data,
                message="Booking rejected successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error rejecting booking: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_applications(self, request):
        """Get tenant's applications"""
        try:
            if request.user.role != 'tenant':
                return APIResponse.forbidden("Only tenants can view their applications")
            
            bookings = Booking.objects.filter(tenant=request.user)
            serializer = BookingSerializer(bookings, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=bookings.count(),
                message="Your applications retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving applications: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def property_applications(self, request):
        """Get applications for landlord's properties"""
        try:
            if request.user.role != 'landlord':
                return APIResponse.forbidden("Only landlords can view property applications")
            
            property_id = request.query_params.get('property_id')
            bookings = Booking.objects.filter(property__landlord=request.user)
            if property_id:
                bookings = bookings.filter(property_id=property_id)
            
            serializer = BookingSerializer(bookings, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=bookings.count(),
                message="Property applications retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving applications: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PropertyVisitViewSet(BaseViewSet):
    """
    Property Visit ViewSet for scheduling property viewings
    """
    serializer_class = PropertyVisitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter visits based on user role"""
        user = self.request.user
        if user.role == 'tenant':
            return PropertyVisit.objects.filter(tenant=user)
        elif user.role == 'landlord':
            return PropertyVisit.objects.filter(property__landlord=user)
        elif user.role == 'admin':
            return PropertyVisit.objects.all()
        return PropertyVisit.objects.none()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def schedule_visit(self, request):
        """Tenant schedules a property visit"""
        try:
            if request.user.role != 'tenant':
                return APIResponse.forbidden("Only tenants can schedule visits")
            
            serializer = PropertyVisitSerializer(data=request.data)
            if serializer.is_valid():
                visit = serializer.save(tenant=request.user)
                return APIResponse.created(
                    data=PropertyVisitSerializer(visit).data,
                    message="Visit scheduled successfully"
                )
            return APIResponse.validation_error("Visit validation failed", serializer.errors)
        except Exception as e:
            return APIResponse.error(f"Error scheduling visit: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def confirm(self, request, pk=None):
        """Landlord confirms property visit"""
        try:
            visit = self.get_object()
            if request.user != visit.property.landlord and request.user.role != 'admin':
                return APIResponse.forbidden("You don't have permission to confirm this visit")
            
            visit.confirmed_by_landlord = True
            visit.landlord_notes = request.data.get('notes', '')
            visit.save()
            
            return APIResponse.success(
                data=PropertyVisitSerializer(visit).data,
                message="Visit confirmed successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error confirming visit: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """Mark property visit as completed"""
        try:
            visit = self.get_object()
            if request.user != visit.tenant and request.user != visit.property.landlord and request.user.role != 'admin':
                return APIResponse.forbidden("You don't have permission to complete this visit")
            
            visit.status = 'completed'
            visit.completed_at = timezone.now()
            visit.save()
            
            return APIResponse.success(
                data=PropertyVisitSerializer(visit).data,
                message="Visit marked as completed"
            )
        except Exception as e:
            return APIResponse.error(f"Error completing visit: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LeaseAgreementViewSet(BaseViewSet):
    """
    Lease Agreement ViewSet
    """
    serializer_class = LeaseAgreementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter lease agreements"""
        user = self.request.user
        if user.role == 'tenant':
            return LeaseAgreement.objects.filter(booking__tenant=user)
        elif user.role == 'landlord':
            return LeaseAgreement.objects.filter(booking__property__landlord=user)
        elif user.role == 'admin':
            return LeaseAgreement.objects.all()
        return LeaseAgreement.objects.none()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_lease(self, request):
        """Create lease agreement from booking"""
        try:
            booking_id = request.data.get('booking_id')
            if not booking_id:
                return APIResponse.bad_request("booking_id is required")
            
            from bookings_app.models import Booking
            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return APIResponse.not_found("Booking not found")
            
            if request.user != booking.property.landlord and request.user.role != 'admin':
                return APIResponse.forbidden("You don't have permission to create a lease for this booking")
            
            contract_number = f"LEA-{uuid.uuid4().hex[:8].upper()}"
            lease = LeaseAgreement.objects.create(
                booking=booking,
                contract_number=contract_number,
                monthly_rent=booking.property.rent_price,
                deposit_amount=booking.property.deposit_required or 0,
                start_date=booking.move_in_date,
                end_date=booking.move_in_date + timedelta(days=booking.lease_term_months*30),
                terms=request.data.get('terms', ''),
                special_conditions=request.data.get('special_conditions', '')
            )
            
            return APIResponse.created(
                data=LeaseAgreementSerializer(lease).data,
                message="Lease agreement created successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error creating lease: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def sign_tenant(self, request, pk=None):
        """Tenant signs lease agreement"""
        try:
            lease = self.get_object()
            if request.user != lease.booking.tenant:
                return APIResponse.forbidden("Only the tenant can sign this lease")
            
            lease.tenant_signed = True
            lease.tenant_signature_date = timezone.now()
            if lease.landlord_signed:
                lease.status = 'signed'
            else:
                lease.status = 'pending_signature'
            lease.save()
            
            return APIResponse.success(
                data=LeaseAgreementSerializer(lease).data,
                message="Lease signed by tenant successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error signing lease: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def sign_landlord(self, request, pk=None):
        """Landlord signs lease agreement"""
        try:
            lease = self.get_object()
            if request.user != lease.booking.property.landlord and request.user.role != 'admin':
                return APIResponse.forbidden("Only the landlord can sign this lease")
            
            lease.landlord_signed = True
            lease.landlord_signature_date = timezone.now()
            if lease.tenant_signed:
                lease.status = 'signed'
            else:
                lease.status = 'pending_signature'
            lease.save()
            
            return APIResponse.success(
                data=LeaseAgreementSerializer(lease).data,
                message="Lease signed by landlord successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error signing lease: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
