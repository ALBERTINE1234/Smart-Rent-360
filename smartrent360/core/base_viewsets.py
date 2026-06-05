"""
Base ViewSets with consistent response formatting
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from .utils import APIResponse


class BaseViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that overrides default list(), create(), retrieve(), update(), and destroy()
    methods to provide consistent response format with status, message, and data.
    """
    
    def list(self, request, *args, **kwargs):
        """Override list to return consistent response format"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return APIResponse.list_response(
                data=serializer.data,
                count=queryset.count(),
                message=f"{self.get_queryset().model.__name__} list retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(
                message=f"Error retrieving {self.get_queryset().model.__name__} list",
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """Override create to return consistent response format"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                return APIResponse.created(
                    data=serializer.data,
                    message=f"{self.get_queryset().model.__name__} created successfully"
                )
            else:
                return APIResponse.validation_error(
                    message="Validation failed",
                    errors=serializer.errors
                )
        except Exception as e:
            return APIResponse.error(
                message=f"Error creating {self.get_queryset().model.__name__}",
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to return consistent response format"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return APIResponse.success(
                data=serializer.data,
                message=f"{self.get_queryset().model.__name__} retrieved successfully"
            )
        except Exception as e:
            if "does not exist" in str(e):
                return APIResponse.not_found(
                    message=f"{self.get_queryset().model.__name__} not found"
                )
            return APIResponse.error(
                message=f"Error retrieving {self.get_queryset().model.__name__}",
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """Override update to return consistent response format"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                self.perform_update(serializer)
                return APIResponse.success(
                    data=serializer.data,
                    message=f"{self.get_queryset().model.__name__} updated successfully"
                )
            else:
                return APIResponse.validation_error(
                    message="Validation failed",
                    errors=serializer.errors
                )
        except Exception as e:
            if "does not exist" in str(e):
                return APIResponse.not_found(
                    message=f"{self.get_queryset().model.__name__} not found"
                )
            return APIResponse.error(
                message=f"Error updating {self.get_queryset().model.__name__}",
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to return consistent response format"""
        try:
            instance = self.get_object()
            model_name = self.get_queryset().model.__name__
            self.perform_destroy(instance)
            return APIResponse.success(
                data=None,
                message=f"{model_name} deleted successfully",
                status_code=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            if "does not exist" in str(e):
                return APIResponse.not_found(
                    message=f"{self.get_queryset().model.__name__} not found"
                )
            return APIResponse.error(
                message=f"Error deleting {self.get_queryset().model.__name__}",
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
