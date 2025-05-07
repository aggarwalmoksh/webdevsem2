from django.db import models
from django.urls import reverse
from django.utils import timezone

class City(models.Model):
    """City model to organize events by location."""
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name}, {self.state}"
    
    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        ordering = ['name']

class Venue(models.Model):
    """Venue model for event locations."""
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='venues')
    capacity = models.PositiveIntegerField()
    is_indoor = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.city.name}"
    
    class Meta:
        verbose_name = 'Venue'
        verbose_name_plural = 'Venues'
        ordering = ['name']

class EventCategory(models.Model):
    """Categories for events (Concert, Theater, Sports, etc.)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Event Category'
        verbose_name_plural = 'Event Categories'
        ordering = ['name']

class Event(models.Model):
    """Main Event model."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='events')
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE, related_name='events')
    banner_image_url = models.URLField()
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    max_seats = models.PositiveIntegerField(default=0)  
    is_indoor_event = models.BooleanField(default=True)
      
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk})
    
    @property
    def is_past_event(self):
        return self.end_date < timezone.now().date()
    
    @property
    def is_ongoing_event(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    
    @property
    def is_upcoming_event(self):
        return self.start_date > timezone.now().date()
    
    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-start_date', 'title']

class SeatCategory(models.Model):
    """Categories for seats (Premium, Standard, etc.)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Seat Category'
        verbose_name_plural = 'Seat Categories'

class Zone(models.Model):
    """Zones for outdoor events (VIP, A, B, General, etc.)."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.event.title} - {self.name}"
    
    @property
    def available_seats(self):
        from bookings.models import Booking
        booked_seats = Booking.objects.filter(zone=self, is_confirmed=True).count()
        return self.capacity - booked_seats
    
    class Meta:
        verbose_name = 'Zone'
        verbose_name_plural = 'Zones'

class Seat(models.Model):
    """Individual seats for indoor events with theater layout."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='seats')
    row = models.CharField(max_length=10)  # A, B, C, etc.
    number = models.PositiveIntegerField()  # 1, 2, 3, etc.
    category = models.ForeignKey(SeatCategory, on_delete=models.CASCADE, related_name='seats')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.event.title} - {self.row}{self.number}"
    
    class Meta:
        verbose_name = 'Seat'
        verbose_name_plural = 'Seats'
        unique_together = ('event', 'row', 'number')
        ordering = ['row', 'number']

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Booking(models.Model):
    user = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    seat_number = models.IntegerField()
    booking_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.event.name}"