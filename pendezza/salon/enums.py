from django.db import models

class BookingStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    NO_SHOW = 'no_show', 'No Show'

class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PARTIAL = 'partial', 'Partially Paid'
    PAID = 'paid', 'Paid'
