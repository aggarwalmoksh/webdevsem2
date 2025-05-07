from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from events.models import Event, Seat, Zone
from accounts.models import User

class Booking(models.Model):
    """Model for event bookings."""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('confirmed', 'Confirmed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, related_name='bookings', null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, related_name='bookings', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)   
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)

    is_confirmed = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    cancellation_date = models.DateTimeField(blank=True, null=True)

    ticket_code = models.CharField(max_length=20, blank=True, null=True, unique=True)
    cancellation_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.user.username} - {self.event.title}"
    
    def clean(self):
        """Validate the booking based on event type and availability."""

        if self.event.is_indoor_event and not self.seat:
            raise ValidationError("Seat must be provided for indoor events.")
        if not self.event.is_indoor_event and not self.zone:
            raise ValidationError("Zone must be provided for outdoor events.")

        if self.seat and self.seat.event != self.event:
            raise ValidationError("Seat does not belong to the selected event.")
        if self.zone and self.zone.event != self.event:
            raise ValidationError("Zone does not belong to the selected event.")

        if self.seat and not self.seat.is_available and not self.pk:
            raise ValidationError("Selected seat is not available.")

        if self.zone:
            available_seats = self.zone.available_seats
            if self.quantity > available_seats:
                raise ValidationError(f"Not enough seats available in this zone. Only {available_seats} left.")
    
    def save(self, *args, **kwargs):

        if not self.total_price:
            if self.seat:
                self.total_price = self.seat.price
            elif self.zone:
                self.total_price = self.zone.price * self.quantity

        if self.is_confirmed and not self.ticket_code:
            from .utils import generate_ticket_code  
            self.ticket_code = generate_ticket_code()

        if self.is_confirmed and self.seat:
            self.seat.is_available = False
            self.seat.save()

        if self.payment_status == 'paid' and not self.payment_date:
            self.payment_date = timezone.now()

        if self.is_cancelled and not self.cancellation_date:
            self.cancellation_date = timezone.now()

            if self.seat:
                self.seat.is_available = True
                self.seat.save()
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-booking_date']

class Payment(models.Model):
    """Model for payment records."""
    PAYMENT_METHOD_CHOICES = [
        ('upi', 'UPI'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment_details')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=Booking.PAYMENT_STATUS_CHOICES)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"Payment #{self.id} - {self.booking.user.username} - {self.amount}"
    
    def save(self, *args, **kwargs):

        self.booking.payment_status = self.payment_status
        self.booking.payment_method = self.payment_method
        self.booking.transaction_id = self.transaction_id
        self.booking.payment_date = self.payment_date

        if self.payment_status == 'paid':
            self.booking.is_confirmed = True
        
        self.booking.save()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    start_time = models.TimeField()

    def __str__(self):
        return self.title



class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=5) #Added rating field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.username} for {self.event.title}"