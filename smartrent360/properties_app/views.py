from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Property, PropertyType, PropertyImage, SavedProperty, PropertyAmenity
from .serializers import (
    PropertySerializer, PropertyTypeSerializer, PropertyImageSerializer,
    SavedPropertySerializer, PropertyAmenitySerializer
)
from core.utils import APIResponse
from core.base_viewsets import BaseViewSet


class PropertyTypeViewSet(BaseViewSet):
    """Property Type ViewSet - Read only"""
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    permission_classes = [AllowAny]


class PropertyViewSet(BaseViewSet):
    """
    Property ViewSet
    - List all properties with filtering
    - Create, update, delete properties (landlords only)
    """
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['listing_type', 'status', 'number_of_rooms', 'country', 'district']
    search_fields = ['title', 'description', 'village', 'street_address']
    ordering_fields = ['created_at', 'rent_price', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter properties based on user role"""
        user = self.request.user
        if user.role == 'landlord':
            return Property.objects.filter(landlord=user)
        return Property.objects.filter(status='available')

    def perform_create(self, serializer):
        """Create property - landlord only"""
        if self.request.user.role != 'landlord':
            raise PermissionError('Only landlords can create properties')
        serializer.save(landlord=self.request.user)

    def perform_update(self, serializer):
        """Update property - landlord only"""
        if self.request.user != serializer.instance.landlord and self.request.user.role != 'admin':
            raise PermissionError('You can only edit your own properties')
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_image(self, request, pk=None):
        """Upload image for property"""
        try:
            property = self.get_object()
            if request.user != property.landlord and request.user.role != 'admin':
                return APIResponse.forbidden("You don't have permission to upload images for this property")
            
            image = request.FILES.get('image')
            if not image:
                return APIResponse.bad_request("Image file is required")
            
            caption = request.data.get('caption', '')
            is_main = request.data.get('is_main_image', False)
            
            property_image = PropertyImage.objects.create(
                property=property,
                image=image,
                caption=caption,
                is_main_image=is_main
            )
            
            return APIResponse.created(
                data=PropertyImageSerializer(property_image).data,
                message="Image uploaded successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error uploading image: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_favorite(self, request, pk=None):
        """Add/remove property from favorites"""
        try:
            property = self.get_object()
            if request.user.role != 'tenant':
                return APIResponse.forbidden("Only tenants can save properties")
            
            saved = SavedProperty.objects.filter(
                tenant=request.user,
                property=property
            ).first()
            
            if saved:
                saved.delete()
                return APIResponse.success(
                    data=None,
                    message="Property removed from favorites"
                )
            else:
                SavedProperty.objects.create(
                    tenant=request.user,
                    property=property
                )
                return APIResponse.success(
                    data=None,
                    message="Property added to favorites"
                )
        except Exception as e:
            return APIResponse.error(f"Error toggling favorite: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_properties(self, request):
        """Get current landlord's properties"""
        try:
            if request.user.role != 'landlord':
                return APIResponse.forbidden("Only landlords can view their properties")
            
            properties = Property.objects.filter(landlord=request.user)
            serializer = PropertySerializer(properties, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=properties.count(),
                message="Your properties retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving properties: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_favorites(self, request):
        """Get current tenant's favorite properties"""
        try:
            saved_properties = SavedProperty.objects.filter(tenant=request.user)
            serializer = SavedPropertySerializer(saved_properties, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=saved_properties.count(),
                message="Your favorite properties retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving favorites: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def view_property(self, request, pk=None):
        """Increment view count for property"""
        try:
            property = self.get_object()
            property.total_views += 1
            property.save(update_fields=['total_views'])
            return APIResponse.success(
                data={'total_views': property.total_views},
                message="View recorded successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error recording view: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def search(self, request):
        """Advanced search with multiple filters"""
        try:
            queryset = Property.objects.filter(status='available')
            
            # Filter by price range
            min_price = request.query_params.get('min_price')
            max_price = request.query_params.get('max_price')
            if min_price:
                queryset = queryset.filter(rent_price__gte=float(min_price))
            if max_price:
                queryset = queryset.filter(rent_price__lte=float(max_price))
            
            # Filter by location
            country = request.query_params.get('country')
            province = request.query_params.get('province')
            district = request.query_params.get('district')
            if country:
                queryset = queryset.filter(country=country)
            if province:
                queryset = queryset.filter(province=province)
            if district:
                queryset = queryset.filter(district=district)
            
            # Filter by room count
            min_rooms = request.query_params.get('min_rooms')
            if min_rooms:
                queryset = queryset.filter(number_of_rooms__gte=int(min_rooms))
            
            serializer = PropertySerializer(queryset, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=queryset.count(),
                message="Properties search completed successfully"
            )
        except ValueError as e:
            return APIResponse.bad_request(f"Invalid filter value: {str(e)}")
        except Exception as e:
            return APIResponse.error(f"Error searching properties: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
