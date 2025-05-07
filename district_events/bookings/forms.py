from django import forms
from .models import Booking
from events.models import Seat, Zone, Feedback  

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['event', 'quantity']

class SeatSelectionForm(forms.Form):
    """Form for selecting seats in theater layout."""
    seat_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event

    def clean_seat_id(self):
        seat_id = self.cleaned_data['seat_id']
        try:
            seat = Seat.objects.get(pk=seat_id, event=self.event)
            if not seat.is_available:
                raise forms.ValidationError("This seat is already booked.")
            return seat_id
        except Seat.DoesNotExist:
            raise forms.ValidationError("Invalid seat selected.")

class ZoneSelectionForm(forms.Form):
    """Form for selecting zones in outdoor layout."""
    zone_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event

    def clean(self):
        cleaned_data = super().clean()
        zone_id = cleaned_data.get('zone_id')
        quantity = cleaned_data.get('quantity')

        if zone_id and quantity:
            try:
                zone = Zone.objects.get(pk=zone_id, event=self.event)
                if zone.available_seats < quantity:
                    raise forms.ValidationError(f"Only {zone.available_seats} seats available in this zone.")
            except Zone.DoesNotExist:
                raise forms.ValidationError("Invalid zone selected.")

        return cleaned_data
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['event', 'rating', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'comments': 'Your Feedback',
            'rating': 'Rating (1-5)',
        }
