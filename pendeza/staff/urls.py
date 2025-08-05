from django.urls import path
from .views import (
    TeamListView, TeamDetailView,
    TeamMemberUpdateView, TeamMemberDeleteView, 
    salon_detail, OwnerStaffListView,
    OwnerStaffCreateView, StaffAvailabilityView
)

app_name = "salon"

urlpatterns = [
    # Public salon views
    path('salon/<int:salon_id>/', salon_detail, name='salon_detail'),
    
    # Team management (public)
    path('<slug:slug>/team/', TeamListView.as_view(), name='team_list'),
    path('<slug:slug>/team/<uuid:pk>/', TeamDetailView.as_view(), name='team_detail'),  # Changed to pk for DetailView
    
    # Owner dashboard views
    path('owner/team/', OwnerStaffListView.as_view(), name='owner_staff_list'),
    path('owner/team/create/', OwnerStaffCreateView.as_view(), name='owner_staff_create'),
    path('owner/<slug:slug>/team/<uuid:staff_id>/edit/', TeamMemberUpdateView.as_view(), name='team_member_update'),
    path('owner/<slug:slug>/team/<uuid:staff_id>/delete/', TeamMemberDeleteView.as_view(), name='team_member_delete'),
    
    # API endpoints
    path('api/staff/availability/', StaffAvailabilityView.as_view(), name='staff_availability'),
]