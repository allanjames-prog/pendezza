from django.contrib import admin
from django.utils.html import format_html
from salon.models import Salon, SalonStatus, SalonGallery, SalonFeatures, SalonFaq, ServiceGender, ServiceCategory, SalonServices, BookingStatus, PaymentStatus, Booking, StaffRole, StaffStatus, StaffOnDuty

class SalonAdmin(admin.ModelAdmin):
    list_per_page = 25
    date_hierarchy = 'date'
    list_display = ['thumbnail', 'name', 'slug', 'user', 'status', 'featured', 'view_count', 'created_at']
    list_display_links = ['thumbnail', 'name']
    list_filter = ['status', 'featured', 'date']
    search_fields = ['name', 'user__username', 'address']
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
            '<img src="/static/images/default-salon.jpg" width="50" height="50" '
            'style="object-fit: cover; border-radius: 4px; opacity: 0.5;"/>'
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


# ======================
# SALON GALLERY ADMIN
# ======================
class SalonGalleryAdmin(admin.ModelAdmin):
    list_display = ['salon', 'thumbnail', 'created_at']
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

admin.site.register(SalonGallery, SalonGalleryAdmin)

# ======================
# SALON FEATURES ADMIN
# ======================
class SalonFeaturesAdmin(admin.ModelAdmin):
    list_display = ['salon', 'icon_type', 'display_icon', 'is_active']
    list_filter = ['icon_type', 'salon']
    search_fields = ['salon__name']
    list_editable = ['is_active']
    list_per_page = 25
    
    def display_icon(self, obj):
        if obj.icon:
            return format_html('<i class="{}"></i> {}', obj.icon_type.lower(), obj.icon)
        return "-"
    display_icon.short_description = 'Icon'

admin.site.register(SalonFeatures, SalonFeaturesAdmin)

# ======================
# SALON FAQ ADMIN
# ======================
class SalonFaqAdmin(admin.ModelAdmin):
    list_display = ['salon', 'truncated_question', 'is_active', 'created_at']
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

admin.site.register(SalonFaq, SalonFaqAdmin)

# ======================
# SALON SERVICES ADMIN
# ======================
class SalonServicesAdmin(admin.ModelAdmin):
    list_display = ['name', 'salon', 'category', 'gender', 'price_display', 'is_active']
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

admin.site.register(SalonServices, SalonServicesAdmin)

# ======================
# BOOKING ADMIN
# ======================
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'salon', 'service', 'user', 'booking_date', 'time_slot', 'status', 'payment_status']
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

admin.site.register(Booking, BookingAdmin)

# ======================
# STAFF ON DUTY ADMIN
# ======================
class StaffOnDutyAdmin(admin.ModelAdmin):
    list_display = ['user', 'salon', 'role', 'status', 'is_active', 'thumbnail']
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

admin.site.register(StaffOnDuty, StaffOnDutyAdmin)