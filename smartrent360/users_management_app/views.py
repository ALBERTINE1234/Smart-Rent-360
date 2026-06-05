from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.db import IntegrityError
from .permissions import IsAdmin, IsLandlord, IsTenant, IsCommissioner
import uuid
from rest_framework_simplejwt.tokens import RefreshToken

from core.utils import APIResponse
from .utils import send_email
from .models import User, LandlordProfile, TenantProfile
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    LandlordProfileSerializer,
    TenantProfileSerializer,
    ChangePasswordSerializer
)
        


# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================

class RegisterView(APIView):
    """
    User Registration Endpoint
    POST: Register new user with email, username, password, role
    Roles: tenant, landlord, commissioner, government, admin
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)

            if not serializer.is_valid():
                return APIResponse.validation_error(
                    "Registration validation failed",
                    errors=serializer.errors
                )

            user = serializer.save()

            # Generate email verification token
            token = str(uuid.uuid4())
            user.email_verification_token = token
            user.is_active = False
            user.is_email_verified = False
            user.save()

            # Send verification email
            verify_link = f"http://127.0.0.1:8000/api/v1/users/verify-email/{token}/"
            send_email(
                "Verify your SmartRent360 account",
                f"Click this link to verify your email: {verify_link}",
                user.email
            )

            return APIResponse.created(
                data=UserSerializer(user).data,
                message="User registered successfully. Check your email to verify your account."
            )

        except IntegrityError as e:
            if 'email' in str(e).lower():
                return APIResponse.conflict("This email is already registered")
            elif 'phone_number' in str(e).lower():
                return APIResponse.conflict("This phone number is already registered")
            return APIResponse.conflict("This data already exists in the system")
        except Exception as e:
            return APIResponse.error(
                f"Error during registration: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyEmailView(APIView):
    """
    Email Verification Endpoint
    GET: Verify email using token sent to email
    """
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            user = get_object_or_404(User, email_verification_token=token)

            user.is_email_verified = True
            user.is_active = True
            user.email_verification_token = None
            user.save()

            return APIResponse.success(
                message="Email verified successfully. You can now login."
            )
        except Exception as e:
            return APIResponse.error(
                f"Error verifying email: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)

            if not serializer.is_valid():
                return APIResponse.validation_error(
                    "Login validation failed",
                    errors=serializer.errors
                )

            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

            user = authenticate(username=email, password=password)

            if not user:
                return APIResponse.unauthorized("Invalid email or password")

            if not user.is_email_verified:
                return APIResponse.forbidden(
                    "Please verify your email first before logging in"
                )

            # 🔥 CREATE JWT TOKENS HERE
            refresh = RefreshToken.for_user(user)

            return APIResponse.success(
                message="Login successful",
                data={
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data
                }
            )

        except Exception as e:
            return APIResponse.error(
                message=f"Error during login: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LogoutView(APIView):
    """
    User Logout Endpoint
    POST: Delete user authentication token
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return APIResponse.success(message="Logout successful")
        except Exception as e:
            return APIResponse.error(
                f"Error during logout: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================
# USER PROFILE ENDPOINTS
# ============================================================

class MeView(APIView):
    """
    Get Current User Profile Endpoint
    GET: Retrieve authenticated user's profile
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            return APIResponse.success(
                data=UserSerializer(request.user).data,
                message="User profile retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(
                f"Error retrieving profile: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateProfileView(APIView):
    """
    Update User Profile Endpoint
    PATCH: Update user profile information
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True
            )

            if not serializer.is_valid():
                return APIResponse.validation_error(
                    "Profile update validation failed",
                    errors=serializer.errors
                )

            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="Profile updated successfully"
            )

        except IntegrityError as e:
            if 'email' in str(e).lower():
                return APIResponse.conflict("This email is already in use")
            elif 'phone_number' in str(e).lower():
                return APIResponse.conflict("This phone number is already in use")
            return APIResponse.conflict("This data already exists")
        except Exception as e:
            return APIResponse.error(
                f"Error updating profile: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================
# PASSWORD MANAGEMENT ENDPOINTS
# ============================================================

class ForgotPasswordView(APIView):
    """
    Forgot Password Endpoint
    POST: Request password reset link
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get("email")

            if not email:
                return APIResponse.bad_request("Email is required")

            user = get_object_or_404(User, email=email)

            # Generate password reset token
            token = str(uuid.uuid4())
            user.password_reset_token = token
            user.save()

            # Send reset link
            reset_link = f"http://127.0.0.1:8000/api/v1/users/reset-password/{token}/"
            send_email(
                "Reset your SmartRent360 Password",
                f"Click here to reset your password: {reset_link}",
                user.email
            )

            return APIResponse.success(
                message="Password reset link sent to your email. Check your inbox."
            )

        except Exception as e:
            return APIResponse.error(
                f"Error processing forgot password: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResetPasswordView(APIView):
    """
    Reset Password Endpoint
    POST: Reset password using token from email
    """
    permission_classes = [AllowAny]

    def post(self, request, token):
        try:
            user = get_object_or_404(User, password_reset_token=token)

            new_password = request.data.get("new_password")
            confirm_password = request.data.get("confirm_password")

            if not new_password or not confirm_password:
                return APIResponse.bad_request(
                    "Both new_password and confirm_password are required"
                )

            if new_password != confirm_password:
                return APIResponse.bad_request(
                    "Passwords do not match"
                )

            if len(new_password) < 8:
                return APIResponse.bad_request(
                    "Password must be at least 8 characters long"
                )

            user.set_password(new_password)
            user.password_reset_token = None
            user.save()

            return APIResponse.success(
                message="Password reset successfully. You can now login with your new password."
            )

        except Exception as e:
            return APIResponse.error(
                f"Error resetting password: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================
# ADMIN ENDPOINTS - USER MANAGEMENT
# ============================================================

class UserListView(APIView):
    """
    List All Users Endpoint
    GET: Admin only - List all users in system
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            users = User.objects.all().order_by('-created_at')
            count = users.count()

            return APIResponse.list_response(
                data=UserSerializer(users, many=True).data,
                count=count,
                message="Users list retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(
                f"Error retrieving users list: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserDetailView(APIView):
    """
    Get User Details Endpoint
    GET: Admin only - Get specific user details
    """
    permission_classes = [IsAdmin]

    def get(self, request, id):
        try:
            user = get_object_or_404(User, id=id)
            return APIResponse.success(
                data=UserSerializer(user).data,
                message="User details retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(
                f"Error retrieving user details: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================
# LANDLORD PROFILE ENDPOINTS
# ============================================================

class LandlordListView(APIView):
    """
    List All Landlords Endpoint
    GET: Admin only - List all landlord profiles
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            profiles = LandlordProfile.objects.all().order_by('-created_at')
            count = profiles.count()

            return APIResponse.list_response(
                data=LandlordProfileSerializer(profiles, many=True).data,
                count=count,
                message="Landlords list retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(
                f"Error retrieving landlords list: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LandlordMyProfileView(APIView):
    """
    Landlord Profile Management Endpoint
    GET: Get current landlord's profile
    PATCH: Update current landlord's profile
    """
    permission_classes = [IsLandlord]

    def get(self, request):
        try:
            profile = get_object_or_404(LandlordProfile, user=request.user)
            return APIResponse.success(
                data=LandlordProfileSerializer(profile).data,
                message="Landlord profile retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(
                f"Error retrieving landlord profile: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request):
        try:
            profile = get_object_or_404(LandlordProfile, user=request.user)

            serializer = LandlordProfileSerializer(
                profile,
                data=request.data,
                partial=True
            )

            if not serializer.is_valid():
                return APIResponse.validation_error(
                    "Landlord profile update validation failed",
                    errors=serializer.errors
                )

            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="Landlord profile updated successfully"
            )

        except Exception as e:
            return APIResponse.error(
                f"Error updating landlord profile: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LandlordDetailView(APIView):
    """
    Get Landlord Details Endpoint
    GET: Admin/Commissioner - Get specific landlord profile
    """
    permission_classes = [IsAdmin | IsCommissioner]

    def get(self, request, id):
        try:
            landlord = get_object_or_404(LandlordProfile, id=id)
            return APIResponse.success(
                data=LandlordProfileSerializer(landlord).data,
                message="Landlord details retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(
                f"Error retrieving landlord details: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyLandlordView(APIView):
    """
    Verify Landlord Endpoint
    POST: Admin/Commissioner only - Verify landlord account
    """
    permission_classes = [IsAdmin | IsCommissioner]

    def post(self, request, id):
        try:
            profile = get_object_or_404(LandlordProfile, id=id)

            if profile.is_verified:
                return APIResponse.conflict(
                    "This landlord is already verified"
                )

            profile.is_verified = True
            profile.verification_status = "approved"
            profile.save()

            # Send verification email to landlord
            send_email(
                "Your SmartRent360 Landlord Account is Verified",
                f"Congratulations! Your landlord account has been verified by our team.",
                profile.user.email
            )

            return APIResponse.success(
                data=LandlordProfileSerializer(profile).data,
                message="Landlord verified successfully"
            )

        except Exception as e:
            return APIResponse.error(
                f"Error verifying landlord: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================
# TENANT PROFILE ENDPOINTS
# ============================================================

class TenantListView(APIView):
    """
    List All Tenants Endpoint
    GET: Admin only - List all tenant profiles
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            profiles = TenantProfile.objects.all().order_by('-created_at')
            count = profiles.count()

            return APIResponse.list_response(
                data=TenantProfileSerializer(profiles, many=True).data,
                count=count,
                message="Tenants list retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(
                f"Error retrieving tenants list: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TenantMyProfileView(APIView):
    """
    Tenant Profile Management Endpoint
    GET: Get current tenant's profile
    PATCH: Update current tenant's profile
    """
    permission_classes = [IsTenant]

    def get(self, request):
        try:
            profile = get_object_or_404(TenantProfile, user=request.user)
            return APIResponse.success(
                data=TenantProfileSerializer(profile).data,
                message="Tenant profile retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(
                f"Error retrieving tenant profile: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request):
        try:
            profile = get_object_or_404(TenantProfile, user=request.user)

            serializer = TenantProfileSerializer(
                profile,
                data=request.data,
                partial=True
            )

            if not serializer.is_valid():
                return APIResponse.validation_error(
                    "Tenant profile update validation failed",
                    errors=serializer.errors
                )

            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="Tenant profile updated successfully"
            )

        except Exception as e:
            return APIResponse.error(
                f"Error updating tenant profile: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TenantDetailView(APIView):
    """
    Get Tenant Details Endpoint
    GET: Admin/Commissioner - Get specific tenant profile
    """
    permission_classes = [IsAdmin | IsCommissioner]

    def get(self, request, id):
        try:
            tenant = get_object_or_404(TenantProfile, id=id)
            return APIResponse.success(
                data=TenantProfileSerializer(tenant).data,
                message="Tenant details retrieved successfully"
            )
        except Exception as e:
            return APIResponse.error(
                f"Error retrieving tenant details: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyTenantView(APIView):
    """
    Verify Tenant Endpoint
    POST: Admin/Commissioner only - Verify tenant account
    """
    permission_classes = [IsAdmin | IsCommissioner]

    def post(self, request, id):
        try:
            profile = get_object_or_404(TenantProfile, id=id)

            if profile.is_verified:
                return APIResponse.conflict(
                    "This tenant is already verified"
                )

            profile.is_verified = True
            profile.verification_status = "approved"
            profile.save()

            # Send verification email to tenant
            send_email(
                "Your SmartRent360 Tenant Account is Verified",
                f"Congratulations! Your tenant account has been verified by our team.",
                profile.user.email
            )

            return APIResponse.success(
                data=TenantProfileSerializer(profile).data,
                message="Tenant verified successfully"
            )

        except Exception as e:
            return APIResponse.error(
                f"Error verifying tenant: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )