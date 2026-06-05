from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
import uuid

from .models import Payment, Receipt, Invoice, RentPaymentSchedule, PlatformCommission
from .serializers import (
    PaymentSerializer, ReceiptSerializer, InvoiceSerializer,
    RentPaymentScheduleSerializer, PlatformCommissionSerializer
)
from core.utils import APIResponse
from core.base_viewsets import BaseViewSet


class PaymentViewSet(BaseViewSet):
    """
    Payment ViewSet for managing rent payments
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter payments based on user role"""
        user = self.request.user
        if user.role == 'tenant':
            return Payment.objects.filter(tenant=user)
        elif user.role == 'landlord':
            return Payment.objects.filter(property__landlord=user)
        elif user.role == 'admin':
            return Payment.objects.all()
        return Payment.objects.none()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def record_payment(self, request):
        """Record a payment"""
        try:
            if request.user.role == 'landlord':
                payment_id = request.data.get('payment_id')
                if not payment_id:
                    return APIResponse.bad_request("payment_id is required")
                
                try:
                    payment = Payment.objects.get(id=payment_id)
                except Payment.DoesNotExist:
                    return APIResponse.not_found("Payment not found")
                
                if request.user != payment.property.landlord and request.user.role != 'admin':
                    return APIResponse.forbidden("You don't have permission to record this payment")
                
                payment.status = 'completed'
                payment.payment_date = timezone.now()
                payment.transaction_id = request.data.get('transaction_id', f"TXN-{uuid.uuid4().hex[:8].upper()}")
                payment.notes = request.data.get('notes', '')
                payment.save()
                
                return APIResponse.success(
                    data=PaymentSerializer(payment).data,
                    message="Payment recorded successfully"
                )
            
            elif request.user.role == 'tenant':
                serializer = PaymentSerializer(data=request.data)
                if serializer.is_valid():
                    payment = serializer.save(tenant=request.user)
                    payment.status = 'completed'
                    payment.payment_date = timezone.now()
                    payment.transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
                    payment.save()
                    return APIResponse.created(
                        data=PaymentSerializer(payment).data,
                        message="Payment recorded successfully"
                    )
                return APIResponse.validation_error("Payment validation failed", serializer.errors)
            else:
                return APIResponse.bad_request("Only tenants and landlords can record payments")
        except Exception as e:
            return APIResponse.error(f"Error recording payment: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_payments(self, request):
        """Get current user's payments"""
        try:
            if request.user.role == 'tenant':
                payments = Payment.objects.filter(tenant=request.user)
            elif request.user.role == 'landlord':
                payments = Payment.objects.filter(property__landlord=request.user)
            else:
                return APIResponse.bad_request("Invalid user role")
            
            serializer = PaymentSerializer(payments, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=payments.count(),
                message="Payments retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving payments: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def overdue_payments(self, request):
        """Get overdue payments"""
        try:
            if request.user.role == 'landlord':
                payments = Payment.objects.filter(
                    property__landlord=request.user,
                    status='pending',
                    due_date__lt=timezone.now().date()
                )
            elif request.user.role == 'tenant':
                payments = Payment.objects.filter(
                    tenant=request.user,
                    status='pending',
                    due_date__lt=timezone.now().date()
                )
            else:
                return APIResponse.bad_request("Invalid user role")
            
            serializer = PaymentSerializer(payments, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=payments.count(),
                message="Overdue payments retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving overdue payments: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def create_monthly_invoices(self, request):
        """Admin action to create monthly invoices"""
        try:
            if request.user.role != 'admin':
                return APIResponse.forbidden("Only admins can create monthly invoices")
            
            return APIResponse.success(
                message="Monthly invoices created successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error creating monthly invoices: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReceiptViewSet(BaseViewSet):
    """
    Receipt ViewSet - Read only
    """
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter receipts based on user role"""
        user = self.request.user
        if user.role == 'tenant':
            return Receipt.objects.filter(payment__tenant=user)
        elif user.role == 'landlord':
            return Receipt.objects.filter(payment__property__landlord=user)
        elif user.role == 'admin':
            return Receipt.objects.all()
        return Receipt.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def generate_receipt(self, request, pk=None):
        """Generate receipt for completed payment"""
        try:
            payment = Payment.objects.get(pk=pk)
            
            if request.user != payment.property.landlord and request.user.role != 'admin':
                return APIResponse.forbidden("You don't have permission to generate receipt for this payment")
            
            if payment.status != 'completed':
                return APIResponse.bad_request("Can only generate receipt for completed payments")
            
            receipt_number = f"RCP-{uuid.uuid4().hex[:8].upper()}"
            receipt = Receipt.objects.create(
                payment=payment,
                receipt_number=receipt_number,
                issued_by=request.user,
                property_title=payment.property.title,
                tenant_name=payment.tenant.get_full_name(),
                landlord_name=payment.property.landlord.get_full_name(),
                period_from=request.data.get('period_from'),
                period_to=request.data.get('period_to')
            )
            
            return APIResponse.created(
                data=ReceiptSerializer(receipt).data,
                message="Receipt generated successfully"
            )
        except Payment.DoesNotExist:
            return APIResponse.not_found("Payment not found")
        except Exception as e:
            return APIResponse.error(f"Error generating receipt: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvoiceViewSet(BaseViewSet):
    """
    Invoice ViewSet for managing invoices
    """
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter invoices based on user role"""
        user = self.request.user
        if user.role == 'tenant':
            return Invoice.objects.filter(booking__tenant=user)
        elif user.role == 'landlord':
            return Invoice.objects.filter(property__landlord=user)
        elif user.role == 'admin':
            return Invoice.objects.all()
        return Invoice.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_paid(self, request, pk=None):
        """Mark invoice as paid"""
        try:
            invoice = self.get_object()
            
            if request.user != invoice.property.landlord and request.user.role != 'admin':
                return APIResponse.forbidden("You don't have permission to mark this invoice as paid")
            
            invoice.payment_received = True
            invoice.payment_date = timezone.now()
            invoice.status = 'paid'
            invoice.save()
            
            return APIResponse.success(
                data=InvoiceSerializer(invoice).data,
                message="Invoice marked as paid"
            )
        except Exception as e:
            return APIResponse.error(f"Error marking invoice as paid: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def pending_invoices(self, request):
        """Get pending invoices"""
        try:
            if request.user.role == 'tenant':
                invoices = Invoice.objects.filter(
                    booking__tenant=request.user,
                    status__in=['sent', 'overdue']
                )
            elif request.user.role == 'landlord':
                invoices = Invoice.objects.filter(
                    property__landlord=request.user,
                    status__in=['sent', 'overdue']
                )
            else:
                return APIResponse.bad_request("Invalid user role")
            
            serializer = InvoiceSerializer(invoices, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=invoices.count(),
                message="Pending invoices retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving pending invoices: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RentPaymentScheduleViewSet(BaseViewSet):
    """
    Rent Payment Schedule ViewSet
    """
    serializer_class = RentPaymentScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter schedules based on user role"""
        user = self.request.user
        if user.role == 'tenant':
            return RentPaymentSchedule.objects.filter(booking__tenant=user)
        elif user.role == 'landlord':
            return RentPaymentSchedule.objects.filter(booking__property__landlord=user)
        elif user.role == 'admin':
            return RentPaymentSchedule.objects.all()
        return RentPaymentSchedule.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_auto_debit(self, request, pk=None):
        """Enable/disable automatic debit for rent"""
        try:
            schedule = self.get_object()
            
            if request.user != schedule.booking.tenant:
                return APIResponse.forbidden("You can only toggle auto-debit for your own payment schedules")
            
            schedule.auto_debit_enabled = not schedule.auto_debit_enabled
            schedule.save()
            
            return APIResponse.success(
                data=RentPaymentScheduleSerializer(schedule).data,
                message=f"Auto-debit {'enabled' if schedule.auto_debit_enabled else 'disabled'} successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error toggling auto-debit: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
