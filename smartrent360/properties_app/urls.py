from django.urls import path
from .views import PropertyViewSet, PropertyTypeViewSet

urlpatterns = [
    # Property endpoints
    path('', PropertyViewSet.as_view({'get': 'list', 'post': 'create'}), name='property-list'),
    path('<int:pk>/', PropertyViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='property-detail'),
    
    # Property Type endpoints
    path('property-types/', PropertyTypeViewSet.as_view({'get': 'list', 'post': 'create'}), name='property-type-list'),
    path('property-types/<int:pk>/', PropertyTypeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='property-type-detail'),
]
