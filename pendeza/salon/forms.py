from django import forms
from django.forms import inlineformset_factory
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Salon, SalonStatus, SalonGallery, SalonFeatures, SalonFaq, 
    ServiceGender, SalonServices, BookingStatus, PaymentStatus,
    StaffRole, StaffStatus, StaffOnDuty, SalonWorkingHours,
    SalonParking, SalonAmenity, SalonPaymentOption
)
from django.contrib.auth.models import User


class SalonServiceForm(forms.ModelForm):
    class Meta:
        model = SalonServices
        fields = [
            'name',
            'description',
            'duration',
            'base_price',
            'women_price',
            'men_price',
            'children_price',
            'category',
            'gender',
            'is_featured',
            'is_active',
            'icon',
            'image',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'category': forms.Select(),
            'gender': forms.Select(),
            'is_featured': forms.CheckboxInput(),
            'is_active': forms.CheckboxInput(),
        }
SalonServiceFormSet = inlineformset_factory(
    Salon,
    SalonServices,
    form=SalonServiceForm,
    extra=1,              # Number of empty forms to display
    can_delete=True       # Allows deletion of services in the formset
)


# ======================
# SALON Register
# ======================
class SalonRegisterForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'description', 'image', 'address', 'mobile', 'email']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Make image field optional if needed
        self.fields['image'].required = False
        
        # Add HTML5 attributes for better UX
        self.fields['mobile'].widget.attrs.update({'pattern': '^\+?1?\d{9,15}$'})
        self.fields['email'].widget.attrs.update({'type': 'email'})

# Add these to your forms.py after SalonRegisterForm

class SalonGalleryForm(forms.ModelForm):
    class Meta:
        model = SalonGallery
        fields = ['image']

SalonGalleryFormSet = forms.inlineformset_factory(
    Salon, SalonGallery, form=SalonGalleryForm,
    extra=5, can_delete=True, max_num=10
)

class SalonFeatureForm(forms.ModelForm):
    class Meta:
        model = SalonFeatures
        fields = ['salon', 'icon_type', 'icon', 'name', 'is_active']

SalonFeatureFormSet = forms.inlineformset_factory(
    Salon, SalonFeatures, form=SalonFeatureForm,
    extra=3, can_delete=True, max_num=10
)

class SalonFaqForm(forms.ModelForm):
    class Meta:
        model = SalonFaq
        fields = ['question', 'answer', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={'placeholder': 'Common question...'}),
            'answer': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Your answer...'}),
        }

SalonFaqFormSet = forms.inlineformset_factory(
    Salon, SalonFaq, form=SalonFaqForm,
    extra=2, can_delete=True, max_num=10
)

class SalonWorkingHoursForm(forms.ModelForm):
    class Meta:
        model = SalonWorkingHours
        fields = ['monday_friday', 'saturday', 'sunday', 'holidays']
        widgets = {
            'monday_friday': forms.TextInput(attrs={'placeholder': '9:00 AM - 7:00 PM'}),
            'saturday': forms.TextInput(attrs={'placeholder': '10:00 AM - 5:00 PM'}),
            'sunday': forms.TextInput(attrs={'placeholder': 'Closed or hours'}),
            'holidays': forms.TextInput(attrs={'placeholder': 'Special holiday hours'}),
        }


# ======================
# SALON GALLERY ADMIN
# ======================
class SalonGalleryInline(admin.TabularInline):
    model = SalonGallery
    list_filter = ['salon']
    search_fields = ['salon__name']
    list_per_page = 25
    readonly_fields = ['thumbnail']
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;"/>',
                obj.image.url
            )
        return "No Image"
    thumbnail.short_description = 'Preview'
    
    def created_at(self, obj):
        return obj.salon.date.strftime("%Y-%m-%d") if obj.salon.date else "-"
    created_at.short_description = 'Created'


# ======================
# SALON FEATURES ADMIN
# ======================
class SalonFeaturesInline(admin.TabularInline):
    model = SalonFeatures
    list_filter = ['icon_type', 'salon']
    search_fields = ['salon__name']
    list_editable = ['is_active']
    list_per_page = 25
    
    def display_icon(self, obj):
        if obj.icon:
            return format_html('<i class="{}"></i> {}', obj.icon_type.lower(), obj.icon)
        return "-"
    display_icon.short_description = 'Icon'


# ======================
# SALON FAQ ADMIN
# ======================
class SalonFaqInline(admin.TabularInline):
    model = SalonFaq
    list_filter = ['is_active', 'salon']
    search_fields = ['question', 'answer', 'salon__name']
    list_editable = ['is_active']
    list_per_page = 25
    
    def truncated_question(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    truncated_question.short_description = 'Question'
    
    def created_at(self, obj):
        return obj.date.strftime("%Y-%m-%d")
    created_at.short_description = 'Created'


# ======================
# SALON SERVICES ADMIN
# ======================
class SalonServicesInline(admin.TabularInline):
    model = SalonServices
    list_filter = ['category', 'gender', 'is_active', 'salon']
    search_fields = ['name', 'description', 'salon__name']
    list_editable = ['is_active']
    list_per_page = 25
    readonly_fields = ['thumbnail']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('salon', 'name', 'category', 'gender', 'is_active')
        }),
        ('Service Details', {
            'fields': ('description', 'duration', 'image')
        }),
        ('Pricing', {
            'fields': ('base_price', 'women_price', 'men_price', 'children_price')
        }),
        ('Visuals', {
            'fields': ('icon', 'thumbnail'),
            'classes': ('collapse',)
        })
    )
    
    def price_display(self, obj):
        prices = []
        if obj.base_price:
            prices.append(f"Base: ${obj.base_price}")
        if obj.women_price:
            prices.append(f"Women: ${obj.women_price}")
        if obj.men_price:
            prices.append(f"Men: ${obj.men_price}")
        if obj.children_price:
            prices.append(f"Kids: ${obj.children_price}")
        return ", ".join(prices)
    price_display.short_description = 'Pricing'
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;"/>',
                obj.image.url
            )
        return "No Image"
    thumbnail.short_description = 'Preview'


# ======================
# STAFF ON DUTY ADMIN
# ======================
from django import forms
from django.forms import inlineformset_factory
from .models import StaffOnDuty, Salon

class StaffForm(forms.ModelForm):
    class Meta:
        model = StaffOnDuty
        fields = [
            'user',
            'role',
            'specialization',
            'bio',
            'hire_date',
            'status',
            'monday_start', 'monday_end',
            'tuesday_start', 'tuesday_end',
            'wednesday_start', 'wednesday_end',
            'thursday_start', 'thursday_end',
            'friday_start', 'friday_end',
            'saturday_start', 'saturday_end',
            'sunday_start', 'sunday_end',
            'break_start',
            'break_duration',
            'profile_pic',
            'display_order',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'specialization': forms.CheckboxSelectMultiple(),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'break_start': forms.TimeInput(attrs={'type': 'time'}),
            'monday_start': forms.TimeInput(attrs={'type': 'time'}),
            'monday_end': forms.TimeInput(attrs={'type': 'time'}),
            'tuesday_start': forms.TimeInput(attrs={'type': 'time'}),
            'tuesday_end': forms.TimeInput(attrs={'type': 'time'}),
            'wednesday_start': forms.TimeInput(attrs={'type': 'time'}),
            'wednesday_end': forms.TimeInput(attrs={'type': 'time'}),
            'thursday_start': forms.TimeInput(attrs={'type': 'time'}),
            'thursday_end': forms.TimeInput(attrs={'type': 'time'}),
            'friday_start': forms.TimeInput(attrs={'type': 'time'}),
            'friday_end': forms.TimeInput(attrs={'type': 'time'}),
            'saturday_start': forms.TimeInput(attrs={'type': 'time'}),
            'saturday_end': forms.TimeInput(attrs={'type': 'time'}),
            'sunday_start': forms.TimeInput(attrs={'type': 'time'}),
            'sunday_end': forms.TimeInput(attrs={'type': 'time'}),
        }

StaffFormSet = inlineformset_factory(
    Salon,
    StaffOnDuty,
    form=StaffForm,
    extra=1,
    can_delete=True
)

class StaffOnDutyInline(admin.TabularInline):
    model = StaffOnDuty
    list_filter = ['role', 'status', 'salon']
    search_fields = ['user__username', 'salon__name']
    list_per_page = 25
    readonly_fields = ['thumbnail']
    
    def is_active(self, obj):
        return obj.status == 'Active'
    is_active.boolean = True
    is_active.short_description = 'Active?'
    
    def thumbnail(self, obj):
        if obj.profile_pic:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;"/>',
                obj.profile_pic.url
            )
        return "No Image"
    thumbnail.short_description = 'Photo'


# ======================
# SALON STATUS ADMIN
# ======================
class SalonStatusAdmin(admin.ModelAdmin):
    list_display = ['salon', 'status', 'created_at']
    model = SalonStatus
    list_filter = ['status', 'salon']
    search_fields = ['salon__name']
    list_per_page = 25
    readonly_fields = ['created_at']

    def created_at(self, obj):
        return obj.date.strftime("%Y-%m-%d") if obj.date else "-"
    created_at.short_description = 'Created'

# ======================
# SERVICE GENDER ADMIN
# ======================
class ServiceGenderAdmin(admin.ModelAdmin):
    model = ServiceGender
    list_filter = ['name']
    search_fields = ['name']
    list_per_page = 25
    readonly_fields = ['created_at']

    def created_at(self, obj):
        return obj.date.strftime("%Y-%m-%d") if obj.date else "-"
    created_at.short_description = 'Created'


# ======================
# BOOKING STATUS ADMIN
# ======================
class BookingStatusAdmin(admin.ModelAdmin):
    model = BookingStatus
    list_filter = ['status', 'payment_status', 'salon']
    search_fields = ['user__username', 'service__name', 'salon__name']
    list_per_page = 25
    date_hierarchy = 'booking_date'
    readonly_fields = ['total_amount_display']

    def booking_id(self, obj):
        return str(obj.id)[:8]
    booking_id.short_description = 'ID'

    def time_slot(self, obj):
        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}" if obj.start_time and obj.end_time else "-"
    time_slot.short_description = 'Time Slot'

    def total_amount_display(self, obj):
        return f"${obj.total_amount}" if obj.total_amount else "-"
    total_amount_display.short_description = 'Total Amount'



# ======================
# STAFF ROLE ADMIN
# ======================
class StaffRoleAdmin(admin.ModelAdmin):
    model = StaffRole
    list_filter = ['name']
    search_fields = ['name']
    list_per_page = 25
    readonly_fields = ['created_at']

    def created_at(self, obj):
        return obj.date.strftime("%Y-%m-%d") if obj.date else "-"
    created_at.short_description = 'Created'


# ======================
# STAFF STATUS ADMIN
# ======================
class StaffStatusAdmin(admin.ModelAdmin):
    model = StaffStatus
    list_filter = ['status', 'user']
    search_fields = ['user__username']
    list_per_page = 25
    readonly_fields = ['created_at']

    def created_at(self, obj):
        return obj.date.strftime("%Y-%m-%d") if obj.date else "-"
    created_at.short_description = 'Created'

 

# ======================
# PAYMENT STATUS ADMIN
# ======================
class PaymentStatusAdmin(admin.ModelAdmin):
    model = PaymentStatus
    list_filter = ['status']
    search_fields = ['booking_id']
    list_per_page = 25
    readonly_fields = ['created_at']

    def created_at(self, obj):
        return obj.date.strftime("%Y-%m-%d") if obj.date else "-"
    created_at.short_description = 'Created'

# ======================
# INLINE ADMIN CLASSES
# ======================

class SalonWorkingHoursInline(admin.StackedInline):
    model = SalonWorkingHours
    extra = 0
    max_num = 1
    fields = ('monday_friday', 'saturday', 'sunday', 'holidays')
    verbose_name = "Working Hours"
    verbose_name_plural = "Working Hours"

class SalonParkingInline(admin.StackedInline):
    model = SalonParking
    extra = 0
    max_num = 1
    fields = ('has_parking', 'parking_details', 'valet_available', 'valet_days')
    verbose_name = "Parking Information"

class SalonAmenityInline(admin.TabularInline):
    model = SalonAmenity
    extra = 1
    fields = ('name', 'description', 'icon', 'is_featured')
    verbose_name = "Amenity"
    verbose_name_plural = "Amenities"

class SalonPaymentOptionInline(admin.TabularInline):
    model = SalonPaymentOption
    extra = 1
    fields = ('method', 'description', 'is_available')
    verbose_name = "Payment Option"
    verbose_name_plural = "Payment Options"


# ======================
# SALON ADMIN
# ======================

class SalonAdmin(admin.ModelAdmin):
    inlines = [SalonGalleryInline, SalonFeaturesInline, SalonFaqInline, SalonServicesInline, StaffOnDutyInline, SalonWorkingHoursInline, SalonParkingInline, SalonAmenityInline, SalonPaymentOptionInline]
    model = Salon
    list_per_page = 25
    date_hierarchy = 'date'
    list_display = ['thumbnail', 'name', 'slug', 'user', 'status', 'featured', 'views', 'date']
    list_display_links = ['thumbnail', 'name']
    list_filter = ['status', 'featured', 'date']
    search_fields = ['name', 'user__username', 'address']
    list_select_related = ['user']
    autocomplete_fields = ['user']
    raw_id_fields = ['tags']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'user', 'status', 'featured')
        }),
        ('Content', {
            'fields': ('description', 'image', 'tags')
        }),
        ('Contact Information', {
            'fields': ('address', 'mobile', 'email')
        }),
        ('Metadata', {
            'fields': ('views', 'date', 'updated_at'),
            'classes': ('collapse',)  # Makes this section collapsible
        })
    )
    readonly_fields = ['date', 'updated_at', 'view_count', 'slug']
    actions = ['make_featured', 'make_live']
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;"/>',
                obj.image.url
            )
        return format_html(
            '<img src="/static/images/default-salon.jpg" width="50" height="50" style="object-fit: cover; border-radius: 4px; opacity: 0.5;"/>'
        )
    thumbnail.short_description = 'Image'
    def view_count(self, obj):
        return obj.views
    view_count.short_description = 'Views'
    def created_at(self, obj):
        return obj.date.strftime("%Y-%m-%d %H:%M")
    created_at.short_description = 'Created'
    def make_featured(self, request, queryset):
        queryset.update(featured=True)
    make_featured.short_description = "Mark selected salons as featured"
    
    def make_live(self, request, queryset):
        queryset.update(status='Live')  
    make_live.short_description = "Mark selected salons as Live"

