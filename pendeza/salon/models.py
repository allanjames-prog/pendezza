from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe
from userauths.models import User
import os, uuid
from django.core.validators import RegexValidator
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

# ============================================
# SALON 
# ============================================
class Salon(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='salons')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=salon_image_upload_path)
    address = models.CharField(max_length=200)
    mobile = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField(max_length=100)
    status = models.CharField(max_length=20, choices=SalonStatus.choices, default=SalonStatus.IN_REVIEW)
    
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
        super(Salon, self).save(*args, **kwargs)
    
    def thumbnail(self):
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" width="60" height="60" '
                'style="object-fit: cover; border-radius: 6px;"/>' %(self.image.url)
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

# Salon Working Hours
class SalonWorkingHours(models.Model):
    salon = models.OneToOneField(Salon, on_delete=models.CASCADE, related_name='working_hours')
    monday_friday = models.CharField(
        max_length=100, 
        default="9AM - 8PM",
        help_text="Format: 9AM - 8PM"
    )
    monday_friday = models.CharField(max_length=100, default="9AM - 8PM")
    saturday = models.CharField(max_length=100, default="9AM - 6PM")
    sunday = models.CharField(max_length=100, default="10AM - 4PM")
    holidays = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Working hours for {self.salon.name}"
    
# Salon Parking
class SalonParking(models.Model):
    salon = models.OneToOneField(Salon, on_delete=models.CASCADE, related_name='parking')
    has_parking = models.BooleanField(default=True)
    parking_details = models.TextField(blank=True)
    valet_available = models.BooleanField(default=False)
    valet_days = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Parking info for {self.salon.name}"

# Salon Amenity
class SalonAmenity(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='amenities')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, 
                           help_text="Font Awesome icon class (e.g. 'fa-wifi')")
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Salon amenities"

    def __str__(self):
        return f"{self.name} at {self.salon.name}"
    
# Salon PaymentOption
class SalonPaymentOption(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='payment_options')
    method = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.method} at {self.salon.name}"

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

# Salon Gallery
class SalonGallery(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to=gallery_image_upload_path)
    salon_gallery_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    

    salon_gallery_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return f"Gallery Image for {self.salon.name}"
    
    class Meta:
        verbose_name_plural = "Salon Gallery"  
        ordering = ['-id']  

# Salon Features
class SalonFeatures(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='features')
    icon_type = models.CharField(max_length=100, null=True, blank=True, choices=ICON_TYPE)
    icon = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True) 
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.name} ({self.salon.name})"  
    
    class Meta:
        verbose_name_plural = "Salon Features" 
        ordering = ['name']
        unique_together = ('salon', 'name')

# Salon FAQs
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
