from django.urls import path
from .views import (
    PaymentViewSet, ReceiptViewSet, InvoiceViewSet,
    RentPaymentScheduleViewSet
)

urlpatterns = [
    # Payment endpoints
    path('', PaymentViewSet.as_view({'get': 'list', 'post': 'create'}), name='payment-list'),
    path('<int:pk>/', PaymentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='payment-detail'),
    
    # Receipt endpoints
    path('receipts/', ReceiptViewSet.as_view({'get': 'list', 'post': 'create'}), name='receipt-list'),
    path('receipts/<int:pk>/', ReceiptViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='receipt-detail'),
    
    # Invoice endpoints
    path('invoices/', InvoiceViewSet.as_view({'get': 'list', 'post': 'create'}), name='invoice-list'),
    path('invoices/<int:pk>/', InvoiceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='invoice-detail'),
    
    # Rent Payment Schedule endpoints
    path('schedules/', RentPaymentScheduleViewSet.as_view({'get': 'list', 'post': 'create'}), name='schedule-list'),
    path('schedules/<int:pk>/', RentPaymentScheduleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='schedule-detail'),
]
