from django.urls import path
from .views import index, salon_detail
from salon import views
from salon.views import SalonGalleryUploadView

app_name = "salon"

urlpatterns = [
  path("", views.index, name="index"),
  path('<slug:slug>/', salon_detail, name='detail'),
  path('<slug:slug>/upload-gallery/', SalonGalleryUploadView.as_view(), name='upload_gallery'),
  path('<slug:slug>/upload-gallery/<int:pk>/', SalonGalleryUploadView.as_view(), name='update_gallery'),
  path('<slug:slug>/upload-gallery/<int:pk>/delete/', SalonGalleryUploadView.as_view(), name='delete_gallery'),
  path('salon/<int:pk>/delete/', views.SalonDeleteView.as_view(), name='salon_delete'),
  path('salon/<int:pk>/update/', views.SalonUpdateView.as_view(), name='salon_update'),
  path('salon/<int:pk>/services/categories/', views.SalonServicesCategoryView.as_view(), name='salon_services_categories'),
  path('salon/<int:pk>/services/categories/<int:category_id>/update/', views.SalonServicesCategoryUpdateView.as_view(), name='salon_services_category_update'),
  path('salon/<int:pk>/services/categories/<int:category_id>/delete/', views.SalonServicesCategoryDeleteView.as_view(), name='salon_services_category_delete'),
  path('salon/<int:pk>/services/categories/<int:category_id>/services/', views.SalonServicesView.as_view(), name='salon_services'),
  path('salon/<int:pk>/services/categories/<int:category_id>/services/<int:service_id>/update/', views.SalonServicesUpdateView.as_view(), name='salon_services_update'),
  path('salon/<int:pk>/services/categories/<int:category_id>/services/<int:service_id>/delete/', views.SalonServicesDeleteView.as_view(), name='salon_services_delete'),
  path('bookings/', views.BookingListView.as_view(), name='booking_list'),
  path('bookings/create/', views.BookingCreateView.as_view(), name='booking_create'),
  path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
  path('bookings/<int:pk>/update/', views.BookingUpdateView.as_view(), name='booking_update'),
  path('bookings/<int:pk>/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),
  path('bookings/<int:pk>/status/', views.BookingStatusUpdateView.as_view(), name='booking_status_update'),
  path('bookings/<int:pk>/payment/', views.PaymentStatusUpdateView.as_view(), name='payment_status_update'),
  path('bookings/calendar/', views.BookingCalendarView.as_view(), name='booking_calendar'),
  path('staff/availability/', views.StaffAvailabilityView.as_view(), name='staff_availability'),


]





































