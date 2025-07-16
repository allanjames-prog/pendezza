from django.contrib import admin
from django.utils.html import format_html

from django import forms
from django.forms import inlineformset_factory
from salon.models import Salon
from staff.models import StaffOnDuty, StaffStatus, StaffRole

# ======================
# STAFF ON DUTY ADMIN
# ======================


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

 