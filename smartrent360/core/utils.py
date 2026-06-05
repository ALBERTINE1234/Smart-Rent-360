"""
Utility functions for consistent API responses
"""
from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """Helper class to create consistent API responses with status, message, and data"""
    
    @staticmethod
    def success(data=None, message="Request successful", status_code=status.HTTP_200_OK):
        """Create a success response"""
        return Response(
            {
                'status': 'success',
                'message': message,
                'data': data
            },
            status=status_code
        )
    
    @staticmethod
    def created(data=None, message="Resource created successfully"):
        """Create a 201 Created response"""
        return Response(
            {
                'status': 'success',
                'message': message,
                'data': data
            },
            status=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def error(message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Create an error response"""
        response_data = {
            'status': 'error',
            'message': message,
            'errors': errors or {}
        }
        return Response(response_data, status=status_code)
    
    @staticmethod
    def bad_request(message="Invalid request data", errors=None):
        """Create a 400 Bad Request response"""
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def unauthorized(message="Unauthorized access"):
        """Create a 401 Unauthorized response"""
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(message="Permission denied"):
        """Create a 403 Forbidden response"""
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def not_found(message="Resource not found"):
        """Create a 404 Not Found response"""
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def conflict(message="Resource conflict"):
        """Create a 409 Conflict response"""
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )
    
    @staticmethod
    def validation_error(message="Validation failed", errors=None):
        """Create a validation error response"""
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @staticmethod
    def list_response(data=None, count=None, message="Data retrieved successfully"):
        """Create a list response with count"""
        response_data = {
            'status': 'success',
            'message': message,
            'count': count or len(data) if data else 0,
            'data': data or []
        }
        return Response(response_data, status=status.HTTP_200_OK)
