from django.contrib import admin
from staff.models import StaffOnDuty, StaffRole, StaffStatus
from django.utils.html import format_html


# ======================
# STAFF ON DUTY ADMIN
# ======================
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
