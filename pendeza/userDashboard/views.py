from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum, Count
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView

# Assuming these are your custom models and enums
from booking.models import Booking, BookingStatus, PaymentStatus
from salon.models import Salon, SalonServices
# Assuming you have a form class for updating services
from salon.forms import SalonServiceForm


# ============================================
# OWNER DASHBOARD
# ============================================
# ========== Ownner Dashboard View ===========
@login_required
def owner_dashboard(request):
    try:
        salon = request.user.salons.get()
    except Salon.DoesNotExist:
        return redirect('salon_register')
    
    # Calculate profile completeness
    completeness = 20  # Base for registration
    
    # Check each profile component and add to completeness score
    if salon.description:
        completeness += 10
    if salon.image:
        completeness += 10
    if hasattr(salon, 'working_hours'):
        completeness += 10
    if salon.services.exists():
        completeness += 10
    if salon.staff_members.exists():
        completeness += 10
    if salon.gallery_images.exists():
        completeness += 10
    if salon.features.exists():
        completeness += 10
    if salon.faqs.exists():
        completeness += 10
    
    # Ensure completeness doesn't exceed 100%
    completeness = min(completeness, 100)
    
    # Get recent bookings (last 5)
    recent_bookings = Booking.objects.filter(
        salon=salon
    ).select_related('service', 'user').order_by('-created_at')[:5]
    
    # Get staff count
    staff_count = salon.staff_members.filter(status='Active').count()
    
    # Get active services count
    active_services = salon.services.filter(is_active=True).count()
    
    # Calculate monthly earnings (only paid bookings)
    current_month = timezone.now().month
    monthly_earnings = Booking.objects.filter(
        salon=salon,
        payment_status=PaymentStatus.PAID,
        booking_date__month=current_month
    ).aggregate(total=Sum('price'))['total'] or 0
    
    # Get next steps for profile completion
    next_steps = get_next_steps(salon)
    
    context = {
        'salon': salon,
        'recent_bookings': recent_bookings,
        'profile_completeness': completeness,
        'next_steps': next_steps,
        'staff_count': staff_count,
        'active_services': active_services,
        'monthly_earnings': monthly_earnings,
        'current_month': timezone.now().strftime('%B'),  # e.g. "January"
        'booking_status_counts': get_booking_status_counts(salon),
    }
    return render(request, 'owner/dashboard.html', context)

def get_next_steps(salon):
    """Helper function to determine next steps for profile completion"""
    next_steps = []
    
    if not salon.description:
        next_steps.append({
            'url': reverse('salon_update', kwargs={'pk': salon.pk}),
            'text': 'Add salon description',
            'icon': 'fas fa-edit'
        })
    if not salon.image:
        next_steps.append({
            'url': reverse('salon_update', kwargs={'pk': salon.pk}),
            'text': 'Upload salon image',
            'icon': 'fas fa-camera'
        })
    if not hasattr(salon, 'working_hours'):
        next_steps.append({
            'url': reverse('salon_update', kwargs={'pk': salon.pk}) + '?section=hours',
            'text': 'Set working hours',
            'icon': 'fas fa-clock'
        })
    if not salon.services.exists():
        next_steps.append({
            'url': reverse('salon_update', kwargs={'pk': salon.pk}) + '?section=services',
            'text': 'Add services',
            'icon': 'fas fa-scissors'
        })
    if not salon.staff_members.exists():
        next_steps.append({
            'url': reverse('salon_update', kwargs={'pk': salon.pk}) + '?section=staff',
            'text': 'Add staff members',
            'icon': 'fas fa-users'
        })
    
    # Return max 3 most important next steps
    return next_steps[:3]

def get_booking_status_counts(salon):
    """Get counts of bookings by status for dashboard stats"""
    status_counts = Booking.objects.filter(salon=salon).values(
        'status'
    ).annotate(
        count=Count('id')
    ).order_by('status')
    
    # Convert to more usable format
    counts_dict = {item['status']: item['count'] for item in status_counts}
    
    # Ensure all statuses are represented
    return {
        'pending': counts_dict.get(BookingStatus.PENDING, 0),
        'confirmed': counts_dict.get(BookingStatus.CONFIRMED, 0),
        'completed': counts_dict.get(BookingStatus.COMPLETED, 0),
        'cancelled': counts_dict.get(BookingStatus.CANCELLED, 0),
    }



# ========== Owner Booking ListView ===========
class OwnerBookingListView(LoginRequiredMixin, ListView):
    template_name = 'owner/bookings/list.html'
    paginate_by = 10

    def get_queryset(self):
        if not hasattr(self.request.user, 'salon'):
            raise PermissionDenied
        return Booking.objects.filter(
            salon=self.request.user.salon
        ).order_by('-booking_date', '-start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = BookingStatus.choices
        return context

# ========== Owner Service ListView ===========
class OwnerServiceListView(LoginRequiredMixin, ListView):
    template_name = 'owner/services/list.html'

    def get_queryset(self):
        if not hasattr(self.request.user, 'salon'):
            raise PermissionDenied
        return SalonServices.objects.filter(
            salon=self.request.user.salon
        ).order_by('category', 'name')

class OwnerServiceUpdateView(LoginRequiredMixin, UpdateView):
    model = SalonServices
    form_class = SalonServiceForm
    template_name = 'owner/services/update.html'

    def get_queryset(self):
        if not hasattr(self.request.user, 'salon'):
            raise PermissionDenied
        return SalonServices.objects.filter(salon=self.request.user.salon)

    def get_success_url(self):
        return reverse('owner_services_list')