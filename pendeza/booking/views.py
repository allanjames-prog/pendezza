# Standard Library

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

# Local Models
from .models import Booking, BookingStatus, PaymentStatus, SalonServices



# ============================================
# BOOKING AND PAYMENT STATUS VIEWS
# ============================================
# ========== BOOKING LIST VIEW ==========
class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'salon/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # For salon owners - show their salon's bookings
        if hasattr(self.request.user, 'salons'):
            salon_ids = self.request.user.salons.values_list('id', flat=True)
            return queryset.filter(salon_id__in=salon_ids)
        
        # For regular users - show only their bookings
        return queryset.filter(user=self.request.user)

# ========== BOOKING CREATE VIEW ==========
class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    template_name = 'salon/booking_form.html'
    fields = ['salon', 'service', 'booking_date', 'start_time', 'gender', 'notes']
    success_url = reverse_lazy('booking_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = BookingStatus.PENDING
        form.instance.payment_status = PaymentStatus.PENDING
        
        # Calculate price based on gender
        service = form.cleaned_data['service']
        form.instance.price = service.get_price_for_gender(form.cleaned_data['gender'])
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = SalonServices.objects.filter(is_active=True)
        return context

# ========== BOOKING DETAIL VIEW ==========
class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'salon/booking_detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_by_user_permission(queryset)

    def filter_by_user_permission(self, queryset):
        booking = get_object_or_404(queryset, pk=self.kwargs['pk'])
        
        # Allow access if user is the booking owner or salon owner
        if self.request.user == booking.user or self.request.user == booking.salon.user:
            return queryset
        raise PermissionDenied

# ========== BOOKING UPDATE VIEW ==========
class BookingUpdateView(LoginRequiredMixin, UpdateView):
    model = Booking
    template_name = 'salon/booking_form.html'
    fields = ['service', 'booking_date', 'start_time', 'gender', 'notes']
    success_url = reverse_lazy('booking_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filter_by_user_permission(queryset)

    def form_valid(self, form):
        if form.instance.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            form.add_error(None, "Only pending or confirmed bookings can be modified")
            return self.form_invalid(form)
        return super().form_valid(form)

# ========== BOOKING DELETE VIEW ==========
class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    template_name = 'salon/booking_confirm_delete.html'
    success_url = reverse_lazy('booking_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

# ========== BOOKING STATUS UPDATE VIEW ==========
class BookingStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        
        # Verify user has permission (salon owner or staff)
        if request.user != booking.salon.user and request.user not in booking.salon.staff_members.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        new_status = request.POST.get('status')
        if new_status not in BookingStatus.values:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        # Validate status transitions
        valid_transitions = {
            BookingStatus.PENDING: [BookingStatus.CONFIRMED, BookingStatus.CANCELLED],
            BookingStatus.CONFIRMED: [BookingStatus.COMPLETED, BookingStatus.CANCELLED, BookingStatus.NO_SHOW],
            # Add other valid transitions as needed
        }
        
        if new_status not in valid_transitions.get(booking.status, []):
            return JsonResponse({'error': 'Invalid status transition'}, status=400)
        
        booking.status = new_status
        booking.save()
        
        return JsonResponse({
            'success': True,
            'new_status': booking.get_status_display(),
            'status_class': self.get_status_class(new_status)
        })

    def get_status_class(self, status):
        status_classes = {
            BookingStatus.PENDING: 'warning',
            BookingStatus.CONFIRMED: 'info',
            BookingStatus.COMPLETED: 'success',
            BookingStatus.CANCELLED: 'danger',
            BookingStatus.NO_SHOW: 'secondary',
        }
        return status_classes.get(status, 'light')

# ========== PAYMENT STATUS UPDATE VIEW ==========
class PaymentStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        
        # Verify user has permission (salon owner or staff)
        if request.user != booking.salon.user and request.user not in booking.salon.staff_members.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        new_status = request.POST.get('status')
        if new_status not in PaymentStatus.values:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        booking.payment_status = new_status
        booking.save()
        
        return JsonResponse({
            'success': True,
            'new_status': booking.get_payment_status_display(),
            'status_class': self.get_status_class(new_status)
        })

    def get_status_class(self, status):
        status_classes = {
            PaymentStatus.PENDING: 'warning',
            PaymentStatus.PAID: 'success',
            PaymentStatus.PARTIAL: 'info',
            PaymentStatus.REFUNDED: 'secondary',
            PaymentStatus.FAILED: 'danger',
        }
        return status_classes.get(status, 'light')

# ========== BOOKING CALENDAR VIEW ==========
class BookingCalendarView(LoginRequiredMixin, View):
    def get(self, request):
        # For salon owners - show their salon's bookings
        if hasattr(request.user, 'salons'):
            salon_ids = request.user.salons.values_list('id', flat=True)
            bookings = Booking.objects.filter(salon_id__in=salon_ids)
        else:
            # For regular users - show only their bookings
            bookings = Booking.objects.filter(user=request.user)
        
        events = []
        for booking in bookings:
            events.append({
                'title': booking.calendar_event_title,
                'start': f"{booking.booking_date}T{booking.start_time}",
                'end': f"{booking.booking_date}T{booking.end_time}",
                'status': booking.status,
                'payment_status': booking.payment_status,
                'url': reverse('booking_detail', kwargs={'pk': booking.pk}),
            })
        
        return JsonResponse(events, safe=False)


