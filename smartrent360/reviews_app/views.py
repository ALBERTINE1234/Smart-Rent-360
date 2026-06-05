from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg, Q
from django.utils import timezone
from users_management_app.models import User
from users_management_app.models import LandlordProfile

from .models import Review, ReviewHelpful, MaintenanceRequest
from .serializers import ReviewSerializer, MaintenanceRequestSerializer
from core.utils import APIResponse
from core.base_viewsets import BaseViewSet


class ReviewViewSet(BaseViewSet):
    """
    Review ViewSet for managing reviews and ratings
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter reviews based on user role and filters"""
        user = self.request.user
        
        # Get filter parameters
        subject = self.request.query_params.get('subject')
        property_id = self.request.query_params.get('property_id')
        landlord_id = self.request.query_params.get('landlord_id')
        status_filter = self.request.query_params.get('status')
        
        queryset = Review.objects.filter(status='published')
        
        if subject:
            queryset = queryset.filter(subject=subject)
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        if landlord_id:
            queryset = queryset.filter(reviewed_landlord_id=landlord_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    def perform_create(self, serializer):
        """Create a review"""
        serializer.save(reviewer=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_review(self, request):
        """Submit a new review"""
        try:
            if request.user.role != 'tenant':
                return APIResponse.forbidden("Only tenants can submit reviews")
            
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                review = serializer.save(reviewer=request.user)
                self._update_ratings(review)
                return APIResponse.created(
                    data=ReviewSerializer(review).data,
                    message="Review submitted successfully"
                )
            return APIResponse.validation_error("Review validation failed", serializer.errors)
        except Exception as e:
            return APIResponse.error(f"Error submitting review: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reply_to_review(self, request, pk=None):
        """Property owner replies to review"""
        try:
            review = self.get_object()
            if request.user != review.reviewed_landlord and request.user.role != 'admin':
                return APIResponse.forbidden("You don't have permission to reply to this review")
            
            reply_text = request.data.get('reply_text', '').strip()
            if not reply_text:
                return APIResponse.bad_request("Reply text is required")
            
            review.response = reply_text
            review.response_date = timezone.now()
            review.save()
            
            return APIResponse.success(
                data=ReviewSerializer(review).data,
                message="Reply added to review successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error replying to review: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_helpful(self, request, pk=None):
        """Mark review as helpful or unhelpful"""
        try:
            review = self.get_object()
            helpful = request.data.get('helpful', True)
            
            vote, created = ReviewHelpful.objects.update_or_create(
                review=review,
                user=request.user,
                defaults={'is_helpful': helpful}
            )
            
            review.helpful_count = review.helpful_votes.filter(is_helpful=True).count()
            review.unhelpful_count = review.helpful_votes.filter(is_helpful=False).count()
            review.save()
            
            message = "Review marked as helpful" if helpful else "Review marked as unhelpful"
            return APIResponse.success(
                data=ReviewSerializer(review).data,
                message=message
            )
        except Exception as e:
            return APIResponse.error(f"Error marking review: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def property_reviews(self, request):
        """Get reviews for a specific property"""
        try:
            property_id = request.query_params.get('property_id')
            if not property_id:
                return APIResponse.bad_request("property_id query parameter is required")
            
            reviews = Review.objects.filter(
                property_id=property_id,
                status='published'
            )
            serializer = ReviewSerializer(reviews, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=reviews.count(),
                message="Property reviews retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving property reviews: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def landlord_reviews(self, request):
        """Get reviews for a specific landlord"""
        try:
            landlord_id = request.query_params.get('landlord_id')
            if not landlord_id:
                return APIResponse.bad_request("landlord_id query parameter is required")
            
            reviews = Review.objects.filter(
                reviewed_landlord_id=landlord_id,
                status='published'
            )
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            
            return APIResponse.success(
                data={
                    'reviews': ReviewSerializer(reviews, many=True).data,
                    'average_rating': avg_rating,
                    'total_reviews': reviews.count()
                },
                message="Landlord reviews retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving landlord reviews: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _update_ratings(self, review):
        """Update ratings on property and landlord"""
        if review.property:
            avg_rating = Review.objects.filter(
                property=review.property,
                status='published'
            ).aggregate(Avg('rating'))['rating__avg']
            
            if avg_rating:
                review.property.rating = avg_rating
                review.property.save(update_fields=['rating'])
        
        if review.reviewed_landlord:
            avg_rating = Review.objects.filter(
                reviewed_landlord=review.reviewed_landlord,
                status='published'
            ).aggregate(Avg('rating'))['rating__avg']
            
            if avg_rating:
                try:
                    landlord_profile = review.reviewed_landlord.landlord_profile
                    landlord_profile.rating = avg_rating
                    landlord_profile.save(update_fields=['rating'])
                except LandlordProfile.DoesNotExist:
                    pass


class MaintenanceRequestViewSet(BaseViewSet):
    """
    Maintenance Request ViewSet
    """
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter maintenance requests based on user role"""
        user = self.request.user
        if user.role == 'tenant':
            return MaintenanceRequest.objects.filter(tenant=user)
        elif user.role == 'landlord':
            return MaintenanceRequest.objects.filter(property__landlord=user)
        elif user.role == 'admin':
            return MaintenanceRequest.objects.all()
        return MaintenanceRequest.objects.none()

    def perform_create(self, serializer):
        """Create maintenance request - tenant only"""
        if self.request.user.role != 'tenant':
            raise PermissionError('Only tenants can create maintenance requests')
        serializer.save(tenant=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def assign(self, request, pk=None):
        """Assign maintenance request to contractor"""
        try:
            request_obj = self.get_object()
            if request.user != request_obj.property.landlord and request.user.role != 'admin':
                return APIResponse.forbidden("You don't have permission to assign this maintenance request")
            
            assigned_to_id = request.data.get('assigned_to_id')
            if not assigned_to_id:
                return APIResponse.bad_request("assigned_to_id is required")
            
            try:
                assigned_to = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                return APIResponse.not_found("User not found")
            
            request_obj.assigned_to = assigned_to
            request_obj.status = 'assigned'
            request_obj.save()
            
            return APIResponse.success(
                data=MaintenanceRequestSerializer(request_obj).data,
                message="Maintenance request assigned successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error assigning maintenance request: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_completed(self, request, pk=None):
        """Mark maintenance request as completed"""
        try:
            request_obj = self.get_object()
            if request.user != request_obj.property.landlord and request.user != request_obj.assigned_to and request.user.role != 'admin':
                return APIResponse.forbidden("You don't have permission to complete this maintenance request")
            
            request_obj.status = 'completed'
            request_obj.completion_notes = request.data.get('completion_notes', '')
            request_obj.completed_at = timezone.now()
            request_obj.save()
            
            return APIResponse.success(
                data=MaintenanceRequestSerializer(request_obj).data,
                message="Maintenance request marked as completed"
            )
        except Exception as e:
            return APIResponse.error(f"Error completing maintenance request: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def open_requests(self, request):
        """Get open maintenance requests"""
        try:
            if request.user.role == 'landlord':
                requests = MaintenanceRequest.objects.filter(
                    property__landlord=request.user,
                    status__in=['open', 'assigned', 'in_progress']
                )
            elif request.user.role == 'tenant':
                requests = MaintenanceRequest.objects.filter(
                    tenant=request.user,
                    status__in=['open', 'assigned', 'in_progress']
                )
            else:
                return APIResponse.bad_request("Invalid user role")
            
            serializer = MaintenanceRequestSerializer(requests, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=requests.count(),
                message="Open maintenance requests retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(f"Error retrieving maintenance requests: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
