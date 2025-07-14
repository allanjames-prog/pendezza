from django.urls import path
from .views import (
    owner_dashboard, OwnerBookingListView, OwnerServiceListView,
    OwnerServiceUpdateView
)

from salon.views import OwnerStaffCreateView, OwnerStaffListView, OwnerStaffCreateView, StaffAvailabilityView

app_name = "userDashboard"

urlpatterns = [
    # Owner URLs
    path('owner/dashboard/', owner_dashboard, name='owner_dashboard'),
    path('owner/bookings/', OwnerBookingListView.as_view(), name='owner_booking_list'),
    path('owner/services/', OwnerServiceListView.as_view(), name='owner_services_list'),
    path('owner/services/<int:pk>/edit/', OwnerServiceUpdateView.as_view(), name='owner_service_update'),
    path('owner/staff/', OwnerStaffListView.as_view(), name='owner_staff_list'),
    path('owner/staff/add/', OwnerStaffCreateView.as_view(), name='owner_staff_create'),
    
    # Staff URLs
    path('staff/availability/', StaffAvailabilityView.as_view(), name='staff_availability'),
]