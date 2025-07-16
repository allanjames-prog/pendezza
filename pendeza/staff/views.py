from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.core.exceptions import PermissionDenied


from salon.models import (
    Salon,
)

from django.urls import reverse


# ===============================================
# SALON TEAM LIST VIEW
# ===============================================
from django.views.generic import ListView, DetailView
from .models import StaffOnDuty

def salon_detail(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    staff_members = salon.staff_members.filter(status='Active').order_by('display_order')[:4]  # Get first 4 active staff
    
    context = {
        'salon': salon,
        'staff_members': staff_members,
        # ... your other context data ...
    }
    return render(request, 'salon_detail.html', context)


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
# ========== SALON TEAM MEMBER UPDATE VIEW ==========
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
    
class OwnerStaffListView(LoginRequiredMixin, ListView):
    template_name = 'owner/staff/list.html'

    def get_queryset(self):
        if not hasattr(self.request.user, 'salon'):
            raise PermissionDenied
        return StaffOnDuty.objects.filter(
            salon=self.request.user.salon
        ).order_by('display_order')

class OwnerStaffCreateView(LoginRequiredMixin, CreateView):
    model = StaffOnDuty
    fields = ['user', 'position', 'bio', 'image', 'display_order', 'status']
    template_name = 'owner/staff/create.html'

    def form_valid(self, form):
        form.instance.salon = self.request.user.salon
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('owner_staff_list')


# ========== STAFF AVAILABILITY CHECK ==========
class StaffAvailabilityView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        print(f"Template: {self.template_name}")
        print(f"Staff count in context: {len(response.context_data['staff_members'])}")
        return response

    def get_staff_working_hours(self, staff, date):
        try:
            staff_on_duty = StaffOnDuty.objects.get(staff_member=staff, date=date)
            return {
                'start': staff_on_duty.start_time,
                'end': staff_on_duty.end_time,
                'break_start': staff_on_duty.break_start_time,
                'break_end': staff_on_duty.break_end_time
            }
        except StaffOnDuty.DoesNotExist:
            return None

    def calculate_available_slots(self, working_hours, existing_bookings, service_duration):
       available_slots = []
       for hour in range(working_hours['start'], working_hours['end']):
           for minute in [0, 30]:
               slot = f"{hour:02}:{minute:02}"
               if slot not in [booking.start_time for booking in existing_bookings]:
                   available_slots.append(slot)
       return available_slots
    
# ========== SALON TEAM MEMBER DELETE VIEW ==========
class TeamMemberDeleteView(LoginRequiredMixin, View):
    def post(self, request, slug, staff_id):
        salon = get_object_or_404(Salon, slug=slug)
        
        # Check if the current user owns the salon
        if request.user != salon.user:
            return JsonResponse({'error': 'You do not have permission to delete this team member'}, status=403)
        
        staff_member = get_object_or_404(StaffOnDuty, id=staff_id, salon=salon)
        staff_member.delete()
        
        return JsonResponse({'success': True, 'message': 'Team member deleted successfully'})
