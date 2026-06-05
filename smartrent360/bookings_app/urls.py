from django.urls import path
from .views import BookingViewSet, PropertyVisitViewSet, LeaseAgreementViewSet

urlpatterns = [
    # Booking endpoints
    path('', BookingViewSet.as_view({'get': 'list', 'post': 'create'}), name='booking-list'),
    path('<int:pk>/', BookingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='booking-detail'),
    
    # Property Visit endpoints
    path('visits/', PropertyVisitViewSet.as_view({'get': 'list', 'post': 'create'}), name='visit-list'),
    path('visits/<int:pk>/', PropertyVisitViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='visit-detail'),
    
    # Lease Agreement endpoints
    path('leases/', LeaseAgreementViewSet.as_view({'get': 'list', 'post': 'create'}), name='lease-list'),
    path('leases/<int:pk>/', LeaseAgreementViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='lease-detail'),
]
