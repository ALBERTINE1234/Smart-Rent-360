"""
URL configuration for smartrent360 project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # USERS MODULE (AUTH + PROFILES)
    path('api/users/', include('users_management_app.urls')),

    # OTHER MODULES
    path('api/properties/', include('properties_app.urls')),
    path('api/bookings/', include('bookings_app.urls')),
    path('api/payments/', include('payments_app.urls')),
    path('api/messaging/', include('messaging_app.urls')),
    path('api/reviews/', include('reviews_app.urls')),

    # DRF LOGIN (optional)
    path('api-auth/', include('rest_framework.urls')),
]

