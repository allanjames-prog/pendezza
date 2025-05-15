from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe
from userauthentication.models import User
import os, uuid, datetime
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta, date, time, datetime
from taggit.managers import TaggableManager


# ============================================
# SALON MODELS
# ============================================
ICON_TYPE = (
    ("Bootstrap Icons", "Bootstrap Icons"),
    ("Fontawesome Icons", "Fontawesome Icons"),
    ("Box Icons", "Box Icons"),
    ("Remi Icons", "Remi Icons"),
    ("Flat Icons", "Flat Icons"),
)
phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'"
)
class SalonStatus(models.TextChoices):
    DRAFT = 'Draft', 'Draft'
    DISABLED = 'Disabled', 'Disabled'
    REJECTED = 'Rejected', 'Rejected'
    IN_REVIEW = 'In Review', 'In Review'
    LIVE = 'Live', 'Live'

# Image upload path 
def salon_image_upload_path(instance, filename):
    """Generate upload path: salon_gallery/<salon_name>/<uuid>.<ext>"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('salon_gallery', slugify(instance.name), filename)

# Salon model
class Salon(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='salons')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=salon_image_upload_path)
    address = models.CharField(max_length=200)
    mobile = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField(max_length=100)
    status = models.CharField(
        max_length=20, 
        choices=SalonStatus.choices, 
        default=SalonStatus.IN_REVIEW
    )
    views = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)
    salon_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Salon'
        verbose_name_plural = 'Salons'

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            unique_id = str(uuid.uuid4())[:5].lower()
            self.slug = f"{slugify(self.name)}-{unique_id}"
        super().save(*args, **kwargs)
    
    def thumbnail(self):
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" width="60" height="60" '
                'style="object-fit: cover; border-radius: 6px;"/>'
            )
        return "No Image"
    
    def salon_gallery(self):
        """Returns the salon gallery images"""
        return SalonGallery.objects.filter(salon=self)
    
    def get_tags_list(self):
        """Returns tags as a list"""
        return [tag.name for tag in self.tags.all()]  # 
    
    @property
    def image_url(self):
        """Returns image URL or None"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None
    

# ============================================
# SALON GALLERY, FEATURES AND FAQs
# ============================================
def gallery_image_upload_path(instance, filename):
    """Generate upload path: salon_gallery/<salon_slug>/<uuid>.<ext>"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    if instance.salon:
        return os.path.join('salon_gallery', instance.salon.slug, filename)
    return os.path.join('salon_gallery', 'no_salon', filename)

class SalonGallery(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to=gallery_image_upload_path)

    def __str__(self):
        return f"Gallery Image for {self.salon.name}"
    
    class Meta:
        verbose_name_plural = "Salon Gallery"  
        ordering = ['-id']  

class SalonFeatures(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='features')
    icon_type = models.CharField(max_length=100, null=True, blank=True, choices=ICON_TYPE)
    icon = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True) 
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.name} ({self.salon.name})"  
    def thumbnail(self):
        if self.icon:
            return mark_safe(
                f'<i class="{self.icon}" style="font-size: 50px;"></i>'
            )
        return "No Icon"
    
    def get_icon_type_display(self):
        """Returns the display name of the icon type"""
        return dict(ICON_TYPE).get(self.icon_type, "Unknown Icon Type")
    
    class Meta:
        verbose_name_plural = "Salon Features" 
        ordering = ['name']
        unique_together = ('salon', 'name')

class SalonFaq(models.Model):  # Fixed spacing
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=1000)
    answer = models.TextField(max_length=1000, null=True, blank=True)  
    is_active = models.BooleanField(default=True) 
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FAQ: {self.question[:50]}..."  
    
    class Meta:
        verbose_name_plural = "Salon FAQs"  
        ordering = ['-date']  


# ============================================
# SALON SERVICES
# ============================================
class ServiceGender(models.TextChoices):
    MEN = 'Men', 'Men'
    WOMEN = 'Women', 'Women'
    CHILDREN = 'Children', 'Children'
    UNISEX = 'Unisex', 'Unisex'

class ServiceCategory(models.TextChoices):
    HAIR = 'Hair', 'Hair'
    NAILS = 'Nails', 'Nails'
    SKINCARE = 'Skincare', 'Skincare'
    WAXING = 'Waxing', 'Waxing'
    MAKEUP = 'Makeup', 'Makeup'
    MASSAGE = 'Massage', 'Massage'
    SPECIALTY = 'Specialty', 'Specialty'

class SalonServices(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    
    # Pricing
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    women_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    men_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    children_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Service metadata
    category = models.CharField(max_length=50, choices=ServiceCategory.choices)
    gender = models.CharField(max_length=20, choices=ServiceGender.choices, default=ServiceGender.UNISEX)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Visual elements
    icon = models.CharField(max_length=100, null=True, blank=True, help_text="Font icon class")
    image = models.ImageField(upload_to='service_images/', null=True, blank=True)
    
    # System fields
    service_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Salon Service"
        verbose_name_plural = "Salon Services"
        ordering = ['category', 'name']
        unique_together = ('salon', 'name')  

    def __str__(self):
        return f"{self.name} ({self.get_category_display()}) - {self.salon.name}"
    
    def get_price_for_gender(self, gender):
        """Returns the appropriate price based on gender"""
        price_map = {
            ServiceGender.WOMEN: self.women_price or self.base_price,
            ServiceGender.MEN: self.men_price or self.base_price,
            ServiceGender.CHILDREN: self.children_price or self.base_price,
            ServiceGender.UNISEX: self.base_price
        }
        return price_map.get(gender, self.base_price)
    
    def thumbnail(self):
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" width="50" height="50" '
                'style="object-fit: cover; border-radius: 4px;"/>'
            )
        return "No Image"

  

# ============================================
# BOOKING AND PAYEMENT STATUS
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
    end_time = models.TimeField(blank=True, null=True)  # Auto-calculated
    gender = models.CharField(max_length=20, choices=ServiceGender.choices)
    notes = models.TextField(blank=True, null=True)
    
    # Status Tracking
    status = models.CharField(
        max_length=20, 
        choices=BookingStatus.choices, 
        default=BookingStatus.PENDING
    )
    payment_status = models.CharField(
        max_length=20, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.PENDING
    )
    
    # Financials
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Staff Assignment
    staff_member = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_bookings'
    )
    
    # System Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancellation_reason = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['booking_date', 'start_time']
        unique_together = ('salon', 'booking_date', 'start_time', 'staff_member')
        indexes = [
            models.Index(fields=['booking_date', 'status']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"Booking #{self.id.hex[:6]} - {self.service.name} ({self.get_status_display()})"

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
    # ... repeat for all weekdays ...
    break_start = models.TimeField(default=time(13, 0))  # Default lunch break
    break_duration = models.PositiveIntegerField(default=60)  # Minutes
    
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
        
        if not getattr(self, start_field) or not getattr(self, end_field):
            return "Not scheduled today"
            
        if getattr(self, start_field) <= current_time <= getattr(self, end_field):
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
    
# ============================================
# SALON REVIEWS
# ============================================
class SalonReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=0)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Salon Review"
        verbose_name_plural = "Salon Reviews"
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.salon.name} by {self.user.get_full_name()}"
    
    def get_rating_display(self):
        """Returns a string representation of the rating"""
        return f"{self.rating} out of 5"
    
    def get_average_rating(self):
        """Returns the average rating for the salon"""
        reviews = self.salon.reviews.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            return total_rating / reviews.count()
        return 0
    
    def get_review_count(self):
        """Returns the total number of reviews for the salon"""
        return self.salon.reviews.count()
    
    def get_user_review(self):
        """Returns the review made by the user"""
        return self.salon.reviews.filter(user=self.user).first()
    
    def get_review_summary(self):
        """Returns a summary of the reviews for the salon"""
        return {
            'average_rating': self.get_average_rating(),
            'review_count': self.get_review_count(),
            'user_review': self.get_user_review()
        }
    
# ============================================
# SALON NOTIFICATIONS
# ============================================
class SalonNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Salon Notification"
        verbose_name_plural = "Salon Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.salon.name} to {self.user.get_full_name()}"
    
    def get_notification_count(self):
        """Returns the total number of notifications for the salon"""
        return self.salon.notifications.count()
    
    def get_unread_notifications(self):
        """Returns unread notifications for the user"""
        return self.user.notifications.filter(is_read=False)
    
    def mark_as_read(self):
        """Marks the notification as read"""
        self.is_read = True
        self.save()

    def mark_all_as_read(self):
        """Marks all notifications for the user as read"""
        self.user.notifications.update(is_read=True)

    def delete_notification(self):
        """Deletes the notification"""
        self.delete()

    def delete_all_notifications(self):
        """Deletes all notifications for the user"""
        self.user.notifications.all().delete()

