from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView
from .models import StaffOnDuty
from salon.models import Salon
from django.urls import reverse


# ===============================================
# SALON TEAM LIST VIEWS
# ===============================================

# A function-based view.
# Shows a salon's details and the first 4 active staff members.
# Used for a public-facing salon profile page.
def salon_detail(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    staff_members = salon.staff_members.filter(status='Active').order_by('display_order')[:3]  # Get first 4 active staff
    
    context = {
        'salon': salon,
        'staff_members': staff_members,
        # ... your other context data ...
    }
    return render(request, 'salon_detail.html', context)

# Shows a list of active staff members for a given salon (based on slug).
# Used for the public team page.
# Filters only status='Active', ordered by display_order.
# Adds the salon object to the context.
class TeamListView(ListView):
    model = StaffOnDuty
    template_name = 'salon/team_list.html'
    context_object_name = 'staff_members'
    
    def get_queryset(self):
        print(f"All staff for salon: {StaffOnDuty.objects.filter(salon__slug=self.kwargs['slug']).count()}")
        print(f"Active staff for salon: {StaffOnDuty.objects.filter(salon__slug=self.kwargs['slug'], status='Active').count()}")
        return StaffOnDuty.objects.filter(
            salon__slug=self.kwargs['slug'],
            status='Active'
        ).select_related('user').prefetch_related('specialization').order_by('display_order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['salon'] = get_object_or_404(Salon, slug=self.kwargs['slug'])
        return context

# Shows details for one specific staff member (if they're active).
# Also uses the slug and staff_id to locate the record.
# Used on a staff member profile page.
class TeamDetailView(DetailView):
    model = StaffOnDuty
    template_name = 'salon/team_detail.html'
    context_object_name = 'staff_member'
    
    def get_object(self, queryset=None):
        return get_object_or_404(
            StaffOnDuty,
            salon__slug=self.kwargs['slug'],
            id=self.kwargs['staff_id'],
            status='Active'
        )
# Lets a logged-in user (salon owner) edit a staff member.
# Only allows editing of specific fields: name, position, bio, etc.
# Ensures the staff belongs to the correct salon before saving.
# Likely used in the owner dashboard for managing staff.
class TeamMemberUpdateView(LoginRequiredMixin, UpdateView):
    model = StaffOnDuty
    template_name = 'salon/team_member_form.html'
    fields = ['name', 'position', 'bio', 'image', 'status']
    
    def get_object(self, queryset=None):
        return get_object_or_404(
            StaffOnDuty,
            salon__slug=self.kwargs['slug'],
            id=self.kwargs['staff_id']
        )
    
    def form_valid(self, form):
        form.instance.salon = get_object_or_404(Salon, slug=self.kwargs['slug'])
        return super().form_valid(form)
    
# Lists all staff for the current logged-in salon owner.
# Protected by LoginRequiredMixin.
# Raises a PermissionDenied if the user doesn’t own a salon.
# Template: 'owner/staff/list.html'.
class OwnerStaffListView(LoginRequiredMixin, ListView):
    template_name = 'owner/staff/list.html'

    def get_queryset(self):
        if not hasattr(self.request.user, 'salon'):
            raise PermissionDenied
        return StaffOnDuty.objects.filter(
            salon=self.request.user.salon
        ).order_by('display_order')


# Allows the salon owner to add a new staff member.
# Automatically links the new staff to the current user’s salon.
# Redirects to the staff list page after success.
class OwnerStaffCreateView(LoginRequiredMixin, CreateView):
    model = StaffOnDuty
    fields = ['user', 'position', 'bio', 'image', 'display_order', 'status']
    template_name = 'owner/staff/create.html'

    def form_valid(self, form):
        form.instance.salon = self.request.user.salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('owner_staff_list')


# Designed to check availability of staff for a given day (but seems incomplete).
# Defines a method to get working hours and another to calculate available slots (30-min intervals).
# Could be used for booking or scheduling features.
# The actual get() implementation is incomplete — right now it just prints and returns super.
class StaffAvailabilityView(LoginRequiredMixin, View):
    """
    View to check staff availability for booking purposes.
    Returns available time slots for staff members on a given date.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for staff availability.
        Expects date and optionally staff_id as query parameters.
        Returns JSON response with available time slots.
        """
        date_str = request.GET.get('date')
        staff_id = request.GET.get('staff_id')
        service_duration = int(request.GET.get('duration', 60))  # default to 60 minutes
        
        if not date_str:
            return JsonResponse({'error': 'Date parameter is required'}, status=400)
        
        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        salon = request.user.salon
        if not salon:
            return JsonResponse({'error': 'User is not associated with a salon'}, status=403)
        
        # Get either specific staff member or all staff for the salon
        if staff_id:
            staff_members = StaffOnDuty.objects.filter(
                id=staff_id,
                salon=salon,
                status='Active'
            )
        else:
            staff_members = StaffOnDuty.objects.filter(
                salon=salon,
                status='Active'
            ).order_by('display_order')
        
        if not staff_members.exists():
            return JsonResponse({'error': 'No active staff members found'}, status=404)
        
        availability_data = {}
        
        for staff in staff_members:
            working_hours = self.get_staff_working_hours(staff, date)
            if not working_hours:
                availability_data[staff.id] = {
                    'name': staff.name,
                    'available': False,
                    'message': 'Not working on this day'
                }
                continue
            
            # Get existing bookings for this staff member on this date
            existing_bookings = staff.bookings.filter(
                date=date,
                status__in=['confirmed', 'pending']
            )
            
            available_slots = self.calculate_available_slots(
                working_hours, 
                existing_bookings, 
                service_duration
            )
            
            availability_data[staff.id] = {
                'name': staff.name,
                'available': bool(available_slots),
                'slots': available_slots,
                'working_hours': {
                    'start': working_hours['start'].strftime('%H:%M'),
                    'end': working_hours['end'].strftime('%H:%M'),
                    'break_start': working_hours['break_start'].strftime('%H:%M') if working_hours['break_start'] else None,
                    'break_end': working_hours['break_end'].strftime('%H:%M') if working_hours['break_end'] else None,
                }
            }
        
        return JsonResponse({
            'date': date_str,
            'staff_availability': availability_data
        })

    def get_staff_working_hours(self, staff, date):
        """
        Retrieve working hours for a staff member on a specific date.
        Returns None if staff is not working that day.
        """
        try:
            staff_on_duty = StaffOnDuty.objects.get(staff_member=staff, date=date)
            return {
                'start': staff_on_duty.start_time,
                'end': staff_on_duty.end_time,
                'break_start': staff_on_duty.break_start_time,
                'break_end': staff_on_duty.break_end_time
            }
        except StaffOnDuty.DoesNotExist:
            # Fall back to default working hours if no specific entry for this date
            if staff.default_working_hours:
                return {
                    'start': staff.default_working_hours.start_time,
                    'end': staff.default_working_hours.end_time,
                    'break_start': staff.default_working_hours.break_start_time,
                    'break_end': staff.default_working_hours.break_end_time
                }
            return None

    def calculate_available_slots(self, working_hours, existing_bookings, service_duration):
        """
        Calculate available time slots based on:
        - Working hours
        - Existing bookings
        - Service duration
        Returns list of available time slots in HH:MM format
        """
        from datetime import datetime, timedelta
        
        available_slots = []
        
        # Convert working hours to datetime objects for calculation
        start_dt = datetime.combine(datetime.today(), working_hours['start'])
        end_dt = datetime.combine(datetime.today(), working_hours['end'])
        
        # Handle break time if exists
        break_start = working_hours.get('break_start')
        break_end = working_hours.get('break_end')
        break_period = None
        if break_start and break_end:
            break_start_dt = datetime.combine(datetime.today(), break_start)
            break_end_dt = datetime.combine(datetime.today(), break_end)
            break_period = (break_start_dt, break_end_dt)
        
        # Get booked slots
        booked_slots = []
        for booking in existing_bookings:
            booking_start = datetime.combine(datetime.today(), booking.start_time)
            booking_end = booking_start + timedelta(minutes=booking.duration)
            booked_slots.append((booking_start, booking_end))
        
        # Generate all possible slots
        current_time = start_dt
        slot_duration = timedelta(minutes=service_duration)
        
        while current_time + slot_duration <= end_dt:
            slot_end = current_time + slot_duration
            
            # Check if slot overlaps with break time
            if break_period and (
                (current_time >= break_period[0] and current_time < break_period[1]) or
                (slot_end > break_period[0] and slot_end <= break_period[1]) or
                (current_time <= break_period[0] and slot_end >= break_period[1])
            ):
                current_time += timedelta(minutes=30)  # move to next slot
                continue
            
            # Check if slot overlaps with any existing booking
            is_available = True
            for booked_start, booked_end in booked_slots:
                if (current_time < booked_end and slot_end > booked_start):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(current_time.strftime('%H:%M'))
            
            current_time += timedelta(minutes=30)  # move to next slot
        
        return available_slots
    
# Allows a salon owner to delete a staff member via AJAX (POST).
# Verifies that the current user is the salon’s owner.
# Returns a JsonResponse indicating success or failure.
# Used in an owner dashboard or admin panel.
class TeamMemberDeleteView(LoginRequiredMixin, View):
    def post(self, request, slug, staff_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to delete this team member'}, status=403)
        
        staff_member = get_object_or_404(StaffOnDuty, id=staff_id, salon=salon)
        staff_member.delete()
        
        return JsonResponse({'success': True, 'message': 'Team member deleted successfully'})
