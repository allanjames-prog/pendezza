from django.urls import path
from .views import index, salon_detail
from salon import views
from salon.views import (
    SalonGalleryUploadView,
    SalonServiceAPIView,
    TeamListView,
    TeamDetailView,
    TeamMemberUpdateView,
    TeamMemberDeleteView,
    SalonDetailView, 
    SalonCreateView, 
    SalonUpdateView, 
    SalonDeleteView
    
)

app_name = "salon"

urlpatterns = [
    
    path('create/', SalonCreateView.as_view(), name='salon_create'),
    path('<slug:slug>/', SalonDetailView.as_view(), name='salon_detail'),
    path('<int:pk>/update/', SalonUpdateView.as_view(), name='salon_update'),
    path('<int:pk>/delete/', SalonDeleteView.as_view(), name='salon_delete'),

    # General
    path("", views.index, name="index"),
    path('<slug:slug>/', salon_detail, name='detail'),
    path('<slug:slug>/', views.salon_detail, name='salon_detail'),

    # Gallery
    path('<slug:slug>/upload-gallery/', SalonGalleryUploadView.as_view(), name='upload_gallery'),
    path('<slug:slug>/upload-gallery/<int:pk>/', SalonGalleryUploadView.as_view(), name='update_gallery'),
    path('<slug:slug>/upload-gallery/<int:pk>/delete/', SalonGalleryUploadView.as_view(), name='delete_gallery'),

    # Salon management
    path('salon/<int:pk>/delete/', views.SalonDeleteView.as_view(), name='salon_delete'),
    path('salon/<int:pk>/update/', views.SalonUpdateView.as_view(), name='salon_update'),

    # Owner URLs
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/bookings/', views.OwnerBookingListView.as_view(), name='owner_booking_list'),
    path('owner/services/', views.OwnerServiceListView.as_view(), name='owner_services_list'),
    path('owner/services/<int:pk>/edit/', views.OwnerServiceUpdateView.as_view(), name='owner_service_update'),
    path('owner/staff/', views.OwnerStaffListView.as_view(), name='owner_staff_list'),
    path('owner/staff/add/', views.OwnerStaffCreateView.as_view(), name='owner_staff_create'),    

    # Bookings
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/update/', views.BookingUpdateView.as_view(), name='booking_update'),
    path('bookings/<int:pk>/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),
    path('bookings/<int:pk>/status/', views.BookingStatusUpdateView.as_view(), name='booking_status_update'),
    path('bookings/<int:pk>/payment/', views.PaymentStatusUpdateView.as_view(), name='payment_status_update'),
    path('bookings/calendar/', views.BookingCalendarView.as_view(), name='booking_calendar'),

    # Staff
    path('staff/availability/', views.StaffAvailabilityView.as_view(), name='staff_availability'),

    # Reviews
    path('<slug:slug>/add-review/', views.add_review, name='salon_review_create'),
    path('<slug:slug>/reviews/', views.SalonReviewsView.as_view(), name='all_reviews'),


    # Services
    path('salon/<slug:slug>/services/', SalonServiceAPIView.as_view(), name='salon-services'),
    path('salon/<slug:slug>/services/<int:service_id>/', SalonServiceAPIView.as_view(), name='salon-service-detail'),
    path('salon/<slug:slug>/services/<int:service_id>/delete/', SalonServiceAPIView.as_view(), name='salon-service-delete'),
    path('salon/<slug:slug>/services/<int:service_id>/update/', SalonServiceAPIView.as_view(), name='salon-service-update'),
    
    path('salon/<slug:slug>/team/', TeamListView.as_view(), name='team_list'),

    # Team
    path('<slug:slug>/team/', TeamListView.as_view(), name='team_list'),
    path('<slug:slug>/team/<uuid:staff_id>/', TeamDetailView.as_view(), name='team_detail'),
    path('<slug:slug>/team/<uuid:staff_id>/update/', TeamMemberUpdateView.as_view(), name='team_member_update'),
    path('<slug:slug>/team/<uuid:staff_id>/delete/', TeamMemberDeleteView.as_view(), name='team_member_delete'),
]
