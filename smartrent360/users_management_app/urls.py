from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
    UpdateProfileView,
    UserListView,
    UserDetailView,
    LandlordListView,
    LandlordMyProfileView,
    LandlordDetailView,
    VerifyLandlordView,
    TenantListView,
    TenantMyProfileView,
    TenantDetailView,
    VerifyTenantView,
    ResetPasswordView,
    ForgotPasswordView,
    VerifyEmailView,
)

urlpatterns = [
    # ============================================================
    # AUTHENTICATION & PROFILE MANAGEMENT
    # ============================================================
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='user_profile'),
    path('update-profile/', UpdateProfileView.as_view(), name='update_profile'),

    # ============================================================
    # EMAIL & PASSWORD MANAGEMENT
    # ============================================================
    path('verify-email/<uuid:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<str:token>/', ResetPasswordView.as_view(), name='reset_password'),


    # ============================================================
    # ADMIN ENDPOINTS - USER MANAGEMENT
    # ============================================================
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:id>/', UserDetailView.as_view(), name='user_detail'),

    # ============================================================
    # LANDLORD PROFILE MANAGEMENT
    # ============================================================
    path('landlords/', LandlordListView.as_view(), name='landlord_list'),
    path('landlords/my-profile/', LandlordMyProfileView.as_view(), name='landlord_my_profile'),
    path('landlords/<int:id>/', LandlordDetailView.as_view(), name='landlord_detail'),
    path('landlords/<int:id>/verify/', VerifyLandlordView.as_view(), name='verify_landlord'),

    # ============================================================
    # TENANT PROFILE MANAGEMENT
    # ============================================================
    path('tenants/', TenantListView.as_view(), name='tenant_list'),
    path('tenants/my-profile/', TenantMyProfileView.as_view(), name='tenant_my_profile'),
    path('tenants/<int:id>/', TenantDetailView.as_view(), name='tenant_detail'),
    path('tenants/<int:id>/verify/', VerifyTenantView.as_view(), name='verify_tenant'),
]
