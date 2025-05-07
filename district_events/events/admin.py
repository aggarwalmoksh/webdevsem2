from django.contrib import admin
from django import forms
from .models import City, Venue, EventCategory, Event, SeatCategory, Zone, Seat

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'is_active')
    list_filter = ('state', 'is_active')
    search_fields = ('name', 'state')

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'capacity', 'is_indoor', 'is_active')
    list_filter = ('city', 'is_indoor', 'is_active')
    search_fields = ('name', 'address', 'city__name')

@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

class SeatInline(admin.TabularInline):
    model = Seat
    extra = 1
    fields = ('row', 'number', 'category', 'price', 'is_available')
    readonly_fields = ('event',)

class ZoneInline(admin.TabularInline):
    model = Zone
    extra = 0
    fields = ('name', 'description', 'capacity', 'price')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'venue', 'category', 'start_date', 'end_date', 'is_published', 'is_featured')
    list_filter = ('venue__city', 'category', 'is_published', 'is_featured', 'is_indoor_event')
    search_fields = ('title', 'description', 'venue__name')
    date_hierarchy = 'start_date'
    inlines = [ZoneInline, SeatInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'category')
        }),
        ('Date and Time', {
            'fields': ('start_date', 'end_date', 'start_time', 'end_time')
        }),
        ('Venue', {
            'fields': ('venue', 'is_indoor_event', 'max_seats')
        }),
        ('Media', {
            'fields': ('banner_image_url',)
        }),
        ('Status', {
            'fields': ('is_published', 'is_featured')
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['generate_seats'] = forms.BooleanField(
                required=False,
                initial=True,
                label="Generate seats automatically (for indoor events)",
                help_text="Check to auto-generate seating"
            )
        return form
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        if not change and obj.is_indoor_event and form.cleaned_data.get('generate_seats', False):
            self.generate_seats(request, obj)
    
    def generate_seats(self, request, event):
        """Generate seats for indoor events"""
        try:
            default_category = SeatCategory.objects.first()
            if not default_category:
                default_category = SeatCategory.objects.create(name='Standard')
            
            seats = []
            for row in range(1, 11):  # Rows A-J
                for seat_num in range(1, 21):  # Seats 1-20 per row
                    seats.append(Seat(
                        event=event,
                        row=chr(64 + row),
                        number=seat_num,
                        category=default_category,
                        price=event.venue.base_price if hasattr(event.venue, 'base_price') else 50.00,
                        is_available=True
                    ))
            
            Seat.objects.bulk_create(seats)
            self.message_user(request, f"Successfully generated {len(seats)} seats for {event.title}")
        except Exception as e:
            self.message_user(request, f"Error generating seats: {str(e)}", level='error')

@admin.register(SeatCategory)
class SeatCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'capacity', 'price')
    list_filter = ('event__venue__city',)
    search_fields = ('name', 'event__title')

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('event', 'row', 'number', 'category', 'price', 'is_available')
    list_filter = ('event', 'category', 'is_available')
    search_fields = ('event__title', 'row', 'number')
    list_editable = ('price', 'is_available')