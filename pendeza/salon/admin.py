from django.contrib import admin
from django.utils.html import format_html
from salon.models import (
    Salon, SalonStatus, SalonGallery, SalonFeatures, 
    SalonFaq, ServiceGender, SalonServices, SalonWorkingHours, SalonParking, 
    SalonAmenity, SalonPaymentOption
)

# Salon
# SalonStatus
# SalonWorkingHours
# SalonParking
# SalonAmenity
# SalonPaymentOption
# SalonGallery
# SalonFeatures
# SalonFaq
# ServiceGender
# ServiceCategory
# SalonServices
# SalonReview
# SalonNotification


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
            'fields': ('thumbnail',),
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
    inlines = [SalonGalleryInline, SalonFeaturesInline, SalonServicesInline]
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
            'classes': ('collapse',) 
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

admin.site.register(Salon, SalonAdmin)

