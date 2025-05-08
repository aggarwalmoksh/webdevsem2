from django import forms
from .models import Event, City, EventCategory,Feedback


class EventSearchForm(forms.Form):
    """Form for searching and filtering events."""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search events...'
        })
    )
    
    city = forms.ModelChoiceField(
        queryset=City.objects.filter(is_active=True),
        required=False,
        empty_label="All Cities",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    category = forms.ModelChoiceField(
        queryset=EventCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    DATE_FILTER_CHOICES = [
        ('', 'Any Date'),
        ('today', 'Today'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('upcoming', 'Upcoming'),
    ]
    
    date_filter = forms.ChoiceField(
        choices=DATE_FILTER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    SORT_CHOICES = [
        ('start_date', 'Date (Soonest)'),
        ('name', 'Name (A-Z)'),
        ('price_low', 'Price (Lowest)'),
        ('price_high', 'Price (Highest)'),
    ]
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='start_date',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

