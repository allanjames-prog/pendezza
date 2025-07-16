from django.contrib import admin
from booking.models import Booking, ActivityLog

# =====================
# Booking Admin
# =====================
class BookingAdmin(admin.ModelAdmin):
    model = Booking
    list_display = ['booking_id', 'user', 'salon', 'service', 'booking_date', 'start_time', 'status', 'payment_status']
    list_filter = ['status', 'payment_status', 'salon']
    search_fields = ['user__username', 'service__name', 'salon__name']
    list_per_page = 25
    date_hierarchy = 'booking_date'
    readonly_fields = ['total_amount_display']

    def booking_id(self, obj):
        return str(obj.booking_id.hex[:8].upper())
    booking_id.short_description = 'ID'

    def time_slot(self, obj):
        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}" if obj.start_time and obj.end_time else "-"
    time_slot.short_description = 'Time Slot'

    def total_amount_display(self, obj):
        return f"${obj.total_amount}" if obj.total_amount else "-"
    total_amount_display.short_description = 'Total Amount'

admin.site.register(Booking, BookingAdmin)

# =====================
# Activity Log Admin
# =====================
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['booking', 'client_in', 'client_out', 'description', 'date']
    list_filter = ['date']
    search_fields = ['booking__user__username', 'description']
    readonly_fields = ['date']

admin.site.register(ActivityLog, ActivityLogAdmin)
