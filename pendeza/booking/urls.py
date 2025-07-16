from django.urls import path
from .views import (
    BookingListView, BookingCreateView, BookingDetailView,
    BookingUpdateView, BookingDeleteView, BookingStatusUpdateView,
    PaymentStatusUpdateView, BookingCalendarView, CurrentBookingsView
)

app_name = "booking"

urlpatterns = [
    # Bookings
    path('bookings/', BookingListView.as_view(), name='booking_list'),
    path('bookings/create/', BookingCreateView.as_view(), name='booking_create'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/update/', BookingUpdateView.as_view(), name='booking_update'),
    path('bookings/<int:pk>/delete/', BookingDeleteView.as_view(), name='booking_delete'),
    path('bookings/<int:pk>/status/', BookingStatusUpdateView.as_view(), name='booking_status_update'),
    path('bookings/<int:pk>/payment/', PaymentStatusUpdateView.as_view(), name='payment_status_update'),
    path('bookings/calendar/', BookingCalendarView.as_view(), name='booking_calendar'),
    path('salon/<int:salon_id>/bookings/', CurrentBookingsView.as_view(), name='current_bookings'),
]