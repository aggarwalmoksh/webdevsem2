from django.contrib import admin
from .models import Booking, Payment

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_date',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'event', 'booking_date', 'total_price', 'payment_status', 'is_confirmed', 'is_cancelled')
    list_filter = ('payment_status', 'is_confirmed', 'is_cancelled', 'event__venue__city')
    search_fields = ('user__username', 'user__email', 'event__title', 'ticket_code')
    date_hierarchy = 'booking_date'
    inlines = [PaymentInline]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'event', 'booking_date')
        }),
        ('Seating', {
            'fields': ('seat', 'zone', 'quantity')
        }),
        ('Payment', {
            'fields': ('total_price', 'payment_status', 'payment_method', 'transaction_id', 'payment_date')
        }),
        ('Status', {
            'fields': ('is_confirmed', 'is_cancelled', 'cancellation_date')
        }),
        ('Ticket', {
            'fields': ('ticket_code',)
        }),
    )
    
    readonly_fields = ('booking_date', 'payment_date', 'cancellation_date')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'payment_method', 'amount', 'payment_status', 'payment_date')
    list_filter = ('payment_method', 'payment_status')
    search_fields = ('booking__user__username', 'booking__user__email', 'transaction_id', 'razorpay_order_id', 'razorpay_payment_id')
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        (None, {
            'fields': ('booking', 'amount', 'currency')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_status', 'transaction_id', 'payment_date')
        }),
        ('Razorpay Details', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
    )
    
    readonly_fields = ('payment_date',)
