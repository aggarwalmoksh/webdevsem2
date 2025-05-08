import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
import requests
from django.conf import settings
from django.core.mail import send_mail
from .models import Event, City, Venue, Zone, Seat, Feedback
from .forms import EventSearchForm 
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required



def home_view(request):
    featured_events = Event.objects.filter(
        is_published=True,
        is_featured=True,
        end_date__gte=timezone.now().date()
    ).order_by('start_date')[:6]

    upcoming_events = Event.objects.filter(
        is_published=True,
        start_date__gt=timezone.now().date()
    ).order_by('start_date')[:8]

    cities = City.objects.filter(is_active=True).order_by('name')

    search_form = EventSearchForm()

    try:
        about_response = requests.get(f"{settings.FLASK_SERVICE_URL}/api/about")
        about_data = about_response.json() if about_response.status_code == 200 else {}
    except requests.exceptions.RequestException:
        about_data = {}

    context = {
        'featured_events': featured_events,
        'upcoming_events': upcoming_events,
        'cities': cities,
        'search_form': search_form,
        'about_data': about_data,
    }
    return render(request, 'home.html', context)



class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        featured_events = Event.objects.filter(
            is_published=True,
            is_featured=True,
            end_date__gte=timezone.now().date()
        ).order_by('start_date')[:6]

        upcoming_events = Event.objects.filter(
            is_published=True,
            start_date__gt=timezone.now().date()
        ).order_by('start_date')[:8]

        cities = City.objects.filter(is_active=True).order_by('name')

        search_form = EventSearchForm()

        try:
            about_response = requests.get(f"{settings.FLASK_SERVICE_URL}/api/about")
            about_data = about_response.json() if about_response.status_code == 200 else {}
        except requests.exceptions.RequestException:
            about_data = {}

        context.update({
            'featured_events': featured_events,
            'upcoming_events': upcoming_events,
            'cities': cities,
            'search_form': search_form,
            'about_data': about_data,
        })

        return context



class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'event'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['form'] = self.form
        print("Context:", context)
        return context
    
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_published=True)

        self.form = EventSearchForm(self.request.GET)

        if self.form.is_valid():
            search_term = self.form.cleaned_data.get('search')
            city = self.form.cleaned_data.get('city')
            category = self.form.cleaned_data.get('category')
            date_filter = self.form.cleaned_data.get('date_filter')

            if search_term:
                queryset = queryset.filter(
                    Q(title__icontains=search_term) | Q(description__icontains=search_term)
                )
            if city:
                queryset = queryset.filter(venue__city=city)
            if category:
                queryset = queryset.filter(category=category)
            if date_filter:
                today = timezone.now().date()
                if date_filter == 'today':
                    queryset = queryset.filter(start_date=today)
                elif date_filter == 'this_week':
                    queryset = queryset.filter(start_date__week=today.isocalendar()[1], start_date__year=today.year)
                elif date_filter == 'this_month':
                    queryset = queryset.filter(start_date__month=today.month, start_date__year=today.year)
                elif date_filter == 'upcoming':
                    queryset = queryset.filter(start_date__gte=today)

            sort_by = self.form.cleaned_data.get('sort_by')
            if sort_by:
                if sort_by == 'price_low':
                    queryset = queryset.annotate(min_price=Min('seats__price'), zone_min_price=Min('zones__price')).order_by(
                        'min_price', 'zone_min_price'
                    )
                elif sort_by == 'price_high':
                    queryset = queryset.annotate(max_price=Max('seats__price'), zone_max_price=Max('zones__price')).order_by(
                        '-max_price', '-zone_max_price'
                    )
                else:
                    queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['search_form'] = EventSearchForm(self.request.GET)
        context['cities'] = City.objects.filter(is_active=True)
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
            'city': self.request.GET.get('city', ''),
            'category': self.request.GET.get('category', ''),
            'date_filter': self.request.GET.get('date_filter', ''),
            'sort_by': self.request.GET.get('sort_by', 'start_date'),
        }
        
        event_list = []
        for event in self.object_list:
            event_list.append({
                'title': event.title,
                'formatted_start_date': event.start_date.strftime("%B %d, %Y"),
                'formatted_end_date': event.end_date.strftime("%B %d, %Y"),
                'location_data': {
                    'name': event.venue.name,
                    'address': event.venue.address,
                }
            })
        context['event_list'] = event_list

        return context



class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()

        if event.is_indoor_event:
            seats = Seat.objects.filter(event=event).order_by('row', 'number')

            seating_map = {}
            for seat in seats:
                if seat.row not in seating_map:
                    seating_map[seat.row] = []
                seating_map[seat.row].append(seat)

            sorted_rows = sorted(seating_map.keys())
            sorted_seating_map = {row: seating_map[row] for row in sorted_rows}

            context['seating_map'] = sorted_seating_map
            context['seat_categories'] = set(seat.category.name for seat in seats)
        else:
            zones = Zone.objects.filter(event=event)
            context['zones'] = zones

        return context


def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return render(request, self.template_name, context)


def get_seats_json(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if event.is_indoor_event:
        seats = Seat.objects.filter(event=event)
        seat_data = [
            {
                'id': seat.id,
                'row': seat.row,
                'number': seat.number,
                'category': seat.category.name,
                'price': float(seat.price),
                'is_available': seat.is_available
            }
            for seat in seats
        ]
    else:
        zones = Zone.objects.filter(event=event)
        seat_data = [
            {
                'id': zone.id,
                'name': zone.name,
                'description': zone.description,
                'capacity': zone.capacity,
                'available_seats': zone.available_seats,
                'price': float(zone.price)
            }
            for zone in zones
        ]

    return JsonResponse({
        'event_id': event.id,
        'event_title': event.title,
        'is_indoor': event.is_indoor_event,
        'seating_data': seat_data
    })



def filter_events_by_city(request):
    city_id = request.GET.get('city_id')

    if city_id:
        events = Event.objects.filter(
            is_published=True,
            venue__city_id=city_id,
            end_date__gte=timezone.now().date()
        ).order_by('start_date')
    else:
        events = Event.objects.filter(
            is_published=True,
            end_date__gte=timezone.now().date()
        ).order_by('start_date')

    events_data = [
        {
            'id': event.id,
            'title': event.title,
            'venue': event.venue.name,
            'start_date': event.start_date.strftime('%d %b %Y'),
            'banner_image_url': event.banner_image_url,
            'url': event.get_absolute_url()
        }
        for event in events[:12]
    ]

    return JsonResponse({'events': events_data})


def test_filter_view(request):
    context = {'my_dict': {'key1': 'value1'}}
    return render(request, 'events/test_filter.html', context)


def privacy_policy_view(request):
    return render(request, 'events/privacy_policy.html')

def terms_view(request):
    return render(request, 'events/terms.html')

def cart_view(request):
    return render(request, 'events/cart.html')

def checkout_view(request):
    return render(request, 'events/checkout.html')

def order_summary_view(request, order_id):
    return render(request, 'events/order_summary.html')

import requests
from django.shortcuts import render

FLASK_API_URL = "http://localhost:5001/api"

def about_us(request):
    try:
        response = requests.get("http://localhost:5001/api/about")
        if response.status_code == 200:
            about_data = response.json()
            return render(request, "about_us.html", {"data": about_data})
        else:
            return render(request, "error.html", {"message": "Error fetching About Us data"})
    except requests.exceptions.RequestException as e:
        return render(request, "error.html", {"message": f"Error: {e}"})
