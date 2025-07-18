import uuid
from datetime import date, datetime, time, timedelta
from django.db import models
from userauths.models import User
from salon.models import Salon, SalonServices
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError


# ============================================
# STAFF ON DUTY (stylists/technicians)
# ============================================
class StaffRole(models.TextChoices):
    HAIR_STYLIST = 'Hair Stylist', 'Hair Stylist'
    NAIL_TECH = 'Nail Technician', 'Nail Technician'
    ESTHETICIAN = 'Esthetician', 'Esthetician'
    BARBER = 'Barber', 'Barber'
    MAKEUP_ARTIST = 'Makeup Artist', 'Makeup Artist'
    MANAGER = 'Manager', 'Manager'
    RECEPTIONIST = 'Receptionist', 'Receptionist'

class StaffStatus(models.TextChoices):
    ACTIVE = 'Active', 'Active'
    ON_LEAVE = 'On Leave', 'On Leave'
    TERMINATED = 'Terminated', 'Terminated'

class StaffOnDuty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='staff_members')

    # Professional Details
    role = models.CharField(max_length=50, choices=StaffRole.choices)
    specialization = models.ManyToManyField(SalonServices, blank=True, related_name='qualified_staff')
    bio = models.TextField(blank=True, null=True)
    hire_date = models.DateField()
    status = models.CharField(max_length=20, choices=StaffStatus.choices, default=StaffStatus.ACTIVE)
    
    # Work Schedule
    monday_start = models.TimeField(default=time(9, 0))
    monday_end = models.TimeField(default=time(17, 0))

    tuesday_start = models.TimeField(default=time(9, 0))
    tuesday_end = models.TimeField(default=time(17, 0))

    wednesday_start = models.TimeField(default=time(9, 0))
    wednesday_end = models.TimeField(default=time(17, 0))

    thursday_start = models.TimeField(default=time(9, 0))
    thursday_end = models.TimeField(default=time(17, 0))

    friday_start = models.TimeField(default=time(9, 0))
    friday_end = models.TimeField(default=time(17, 0))

    saturday_start = models.TimeField(null=True, blank=True)  
    saturday_end = models.TimeField(null=True, blank=True)

    sunday_start = models.TimeField(null=True, blank=True)  
    sunday_end = models.TimeField(null=True, blank=True)
   
    break_start = models.TimeField(default=time(13, 0)) 
    break_duration = models.PositiveIntegerField(default=60) 
    
    # Visual Elements
    profile_pic = models.ImageField(upload_to='staff_profile_pics/', blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    
    # System Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    class Meta:
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff On Duty"
        ordering = ['display_order', 'user__first_name']
        unique_together = ('user', 'salon')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()} at {self.salon.name}"

    @property
    def current_status(self):
        """Check if staff is currently working based on schedule"""
        now = timezone.now()
        current_time = now.time()
        current_day = now.strftime('%A').lower()
        
        start_field = f"{current_day}_start"
        end_field = f"{current_day}_end"
        
        # Skip if the day fields don't exist or are None
        if not hasattr(self, start_field) or not hasattr(self, end_field):
            return "Not scheduled"
            
        start_time = getattr(self, start_field)
        end_time = getattr(self, end_field)
        
        if start_time is None or end_time is None:
            return "Not scheduled today"
            
        if start_time <= current_time <= end_time:
            if self.break_start and self.break_duration:
                break_end = (datetime.combine(date.today(), self.break_start) + 
                        timedelta(minutes=self.break_duration)).time()
                if self.break_start <= current_time <= break_end:
                    return "On break"
            return "On duty"
        return "Off duty"

    def get_todays_schedule(self):
        """Returns today's work hours"""
        today = timezone.now().strftime('%A').lower()
        return {
            'start': getattr(self, f"{today}_start"),
            'end': getattr(self, f"{today}_end"),
            'break_start': self.break_start,
            'break_end': (datetime.combine(date.today(), self.break_start) + 
                         timedelta(minutes=self.break_duration)).time()
        }

    def get_qualified_services(self):
        """Returns services this staff member is qualified to perform"""
        return self.specialization.all()

    def thumbnail(self):
        if self.profile_pic:
            return mark_safe(
                f'<img src="{self.profile_pic.url}" width="50" height="50" '
                'style="object-fit: cover; border-radius: 50%;"/>'
            )
        return "No Image"

    def get_profile_pic_url(self):
        """Returns profile picture URL or None"""
        if self.profile_pic and hasattr(self.profile_pic, 'url'):
            return self.profile_pic.url
        return None
    
    def clean(self):
        if not self.user.get_full_name().strip():
            raise ValidationError("Associated user must have a first or last name set")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
