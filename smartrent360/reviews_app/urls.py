from django.urls import path
from .views import ReviewViewSet, MaintenanceRequestViewSet

urlpatterns = [
    # Review endpoints
    path('', ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='review-list'),
    path('<int:pk>/', ReviewViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='review-detail'),
    
    # Maintenance Request endpoints
    path('maintenance/', MaintenanceRequestViewSet.as_view({'get': 'list', 'post': 'create'}), name='maintenance-list'),
    path('maintenance/<int:pk>/', MaintenanceRequestViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='maintenance-detail'),
]
