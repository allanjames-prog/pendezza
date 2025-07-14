# Standard Library
import uuid
from datetime import datetime, timedelta

# Django
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Local
from salon.models import Salon, SalonServices
from userauths.models import User
from salon.models import ServiceGender




# ============================================
# BOOKING AND PAYMENT STATUS
# ============================================
class BookingStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    CONFIRMED = 'Confirmed', 'Confirmed'
    COMPLETED = 'Completed', 'Completed'
    CANCELLED = 'Cancelled', 'Cancelled'
    NO_SHOW = 'No Show', 'No Show'

class PaymentStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    PAID = 'Paid', 'Paid'
    PARTIAL = 'Partial', 'Partial'
    REFUNDED = 'Refunded', 'Refunded'
    FAILED = 'Failed', 'Failed'

class Booking(models.Model):
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(SalonServices, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salon_bookings')
    
    # Booking Details
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=ServiceGender.choices)
    notes = models.TextField(blank=True, null=True)
    
    # Status Tracking
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    
    # Financials
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Staff Assignment
    staff_member = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bookings', limit_choices_to={'groups__name': 'Staff'})
    
    # System Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)  # For tracking

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['booking_date', 'start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['salon', 'booking_date', 'start_time', 'staff_member'],
                name='unique_staff_booking'
            ),
            models.CheckConstraint(
                check=models.Q(booking_date__gte=timezone.now().date()),
                name='booking_date_cannot_be_in_past'
            ),
        ]
        indexes = [
            models.Index(fields=['booking_date', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['staff_member', 'booking_date']),
        ]

    def __str__(self):
        return f"Booking #{self.booking_id.hex[:6].upper()} - {self.service.name} ({self.get_status_display()})"

    def clean(self):
        # Validate booking date is not in the past
        if self.booking_date and self.booking_date < timezone.now().date():
            raise ValidationError("Booking date cannot be in the past")
        
        # Validate staff member belongs to the salon
        if self.staff_member and not self.salon.staff_members.filter(id=self.staff_member.id).exists():
            raise ValidationError("Selected staff member doesn't belong to this salon")

    def save(self, *args, **kwargs):
        # Auto-calculate end time based on service duration
        if not self.end_time and self.service.duration:
            start_datetime = datetime.combine(self.booking_date, self.start_time)
            end_datetime = start_datetime + timedelta(minutes=self.service.duration)
            self.end_time = end_datetime.time()
        
        # Auto-set price based on gender
        if not self.price:
            self.price = self.service.get_price_for_gender(self.gender)
        
        # Calculate total amount
        self.total_amount = self.price - self.discount + self.tax
        
        # Update payment status based on amount paid
        if self.amount_paid >= self.total_amount:
            self.payment_status = PaymentStatus.PAID
        elif self.amount_paid > 0:
            self.payment_status = PaymentStatus.PARTIAL
        
        super().save(*args, **kwargs)

    def get_duration(self):
        """Returns duration in minutes"""
        if self.end_time:
            start = datetime.combine(self.booking_date, self.start_time)
            end = datetime.combine(self.booking_date, self.end_time)
            return int((end - start).total_seconds() / 60)
        return self.service.duration

    def is_upcoming(self):
        today = timezone.now().date()
        now = timezone.now().time()
        if self.booking_date > today:
            return True
        return self.booking_date == today and self.start_time > now

    @property
    def calendar_event_title(self):
        return f"{self.service.name} - {self.user.get_full_name() or self.user.username}"

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

    def can_be_modified(self):
        return self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]

    def get_status_badge(self):
        status_classes = {
            BookingStatus.PENDING: 'bg-warning',
            BookingStatus.CONFIRMED: 'bg-info',
            BookingStatus.COMPLETED: 'bg-success',
            BookingStatus.CANCELLED: 'bg-danger',
            BookingStatus.NO_SHOW: 'bg-secondary',
        }
        return status_classes.get(self.status, 'bg-light text-dark')

    def get_payment_status_badge(self):
        status_classes = {
            PaymentStatus.PENDING: 'bg-warning',
            PaymentStatus.PAID: 'bg-success',
            PaymentStatus.PARTIAL: 'bg-primary',
            PaymentStatus.REFUNDED: 'bg-secondary',
            PaymentStatus.FAILED: 'bg-danger',
        }
        return status_classes.get(self.payment_status, 'bg-light text-dark')