from django.urls import path
from .views import index, salon_detail
from salon import views
from salon.views import SalonGalleryUploadView, SalonServiceAPIView, TeamListView, TeamDetailView, TeamMemberUpdateView, TeamMemberDeleteView

app_name = "salon"

urlpatterns = [
  path("", views.index, name="index"),
  path('<slug:slug>/', salon_detail, name='detail'),
  path('<slug:slug>/upload-gallery/', SalonGalleryUploadView.as_view(), name='upload_gallery'),
  path('<slug:slug>/upload-gallery/<int:pk>/', SalonGalleryUploadView.as_view(), name='update_gallery'),
  path('<slug:slug>/upload-gallery/<int:pk>/delete/', SalonGalleryUploadView.as_view(), name='delete_gallery'),
  path('salon/<int:pk>/delete/', views.SalonDeleteView.as_view(), name='salon_delete'),
  path('salon/<int:pk>/update/', views.SalonUpdateView.as_view(), name='salon_update'),
  path('bookings/', views.BookingListView.as_view(), name='booking_list'),
  path('bookings/create/', views.BookingCreateView.as_view(), name='booking_create'),
  path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
  path('bookings/<int:pk>/update/', views.BookingUpdateView.as_view(), name='booking_update'),
  path('bookings/<int:pk>/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),
  path('bookings/<int:pk>/status/', views.BookingStatusUpdateView.as_view(), name='booking_status_update'),
  path('bookings/<int:pk>/payment/', views.PaymentStatusUpdateView.as_view(), name='payment_status_update'),
  path('bookings/calendar/', views.BookingCalendarView.as_view(), name='booking_calendar'),
  path('staff/availability/', views.StaffAvailabilityView.as_view(), name='staff_availability'),
  path('add-review/', views.add_review, name='add_review'),
  path('<slug:slug>/add-review/', views.add_review, name='salon_review_create'),
  path('salon/<slug:slug>/services/', SalonServiceAPIView.as_view(), name='salon-services'),
  path('salon/<slug:slug>/services/<int:service_id>/', SalonServiceAPIView.as_view(), name='salon-service-detail'),
  path('salon/<slug:slug>/services/<int:service_id>/delete/', SalonServiceAPIView.as_view(), name='salon-service-delete'),
  path('salon/<slug:slug>/services/<int:service_id>/update/', SalonServiceAPIView.as_view(), name='salon-service-update'),

  path('<slug:slug>/team/', TeamListView.as_view(), name='team_list'),
  path('<slug:slug>/team/<uuid:staff_id>/', TeamDetailView.as_view(), name='team_detail'),
  path('<slug:slug>/team/<uuid:staff_id>/update/', TeamMemberUpdateView.as_view(), name='team_member_update'),
  path('<slug:slug>/team/<uuid:staff_id>/delete/', TeamMemberDeleteView.as_view(), name='team_member_delete'),
  path('salon/<uuid:pk>/add-review/', views.add_review, name='add_review'),
  
  path('<slug:slug>/', views.salon_detail, name='salon_detail'),
  path('<slug:slug>/add-review/', views.add_review, name='add_review'),



]






































