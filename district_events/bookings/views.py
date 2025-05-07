import razorpay
import json
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Event, Feedback
from .forms import FeedbackForm,BookingForm
from .models import Booking, Payment
from events.models import Event, Seat, Zone
from .forms import BookingForm
from .utils import generate_ticket_code, generate_pdf_ticket

class SeatSelectionView(LoginRequiredMixin, View):
    """View for selecting seats/zones for an event."""
    template_name = 'bookings/seat_selection.html'

    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id, is_published=True)

        if event.end_date < timezone.now().date():
            messages.error(request, 'This event has already ended.')
            return redirect('events:event_detail', pk=event_id)

        context = {
            'event': event,
        }

        if event.is_indoor_event:
            seats = Seat.objects.filter(event=event).order_by('row', 'number')

            seating_map = {}
            for seat in seats:
                if seat.row not in seating_map:
                    seating_map[seat.row] = []
                seating_map[seat.row].append(seat)

            sorted_rows = sorted(seating_map.keys())
            context['rows'] = sorted_rows
            context['seating_map'] = seating_map
            context['seat_categories'] = set(seat.category for seat in seats)

        else:
            zones = Zone.objects.filter(event=event)

            for zone in zones:
                if zone.capacity > 0:
                    zone.available_percentage = int((zone.available_seats / zone.capacity) * 100)
                else:
                    zone.available_percentage = 0
            context['zones'] = zones

        return render(request, self.template_name, context)

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id, is_published=True)

        if event.is_indoor_event:
          
            seat_id = request.POST.get('seat_id')
            if not seat_id:
                messages.error(request, 'Please select a seat.')
                return redirect('bookings:seat_selection', event_id=event_id)

            seat = get_object_or_404(Seat, pk=seat_id, event=event)

        
            if not seat.is_available:
                messages.error(request, 'Sorry, this seat is already booked.')
                return redirect('bookings:seat_selection', event_id=event_id)

        
            booking = Booking.objects.create(
                user=request.user,
                event=event,
                seat=seat,
                total_price=seat.price,
                quantity=1
            )

        else:

            zone_id = request.POST.get('zone_id')
            quantity = request.POST.get('quantity', '1')

            if not zone_id:
                messages.error(request, 'Please select a zone.')
                return redirect('bookings:seat_selection', event_id=event_id)

            try:
                quantity = int(quantity)
                if quantity < 1:
                    raise ValueError
            except ValueError:
                messages.error(request, 'Please enter a valid quantity.')
                return redirect('bookings:seat_selection', event_id=event_id)

            zone = get_object_or_404(Zone, pk=zone_id, event=event)

            if zone.available_seats < quantity:
                messages.error(request, f'Sorry, only {zone.available_seats} seats are available in this zone.')
                return redirect('bookings:seat_selection', event_id=event_id)

            booking = Booking.objects.create(
                user=request.user,
                event=event,
                zone=zone,
                quantity=quantity,
                total_price=zone.price * quantity
            )
        return redirect('bookings:payment', booking_id=booking.id)

class PaymentView(LoginRequiredMixin, View):
    """View for handling payments."""
    template_name = 'bookings/payment.html'

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

        if booking.payment_status == 'paid':
            return redirect('bookings:booking_confirmation', booking_id=booking.id)

        if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            try:
                amount = int(booking.total_price * 100) 
                order_currency = 'INR'
                order_receipt = f'booking_{booking.id}'

                order_data = {
                    'amount': amount,
                    'currency': order_currency,
                    'receipt': order_receipt,
                    'payment_capture': 1  
                }

                razorpay_order = client.order.create(data=order_data)
                razorpay_order_id = razorpay_order['id']

            
                payment, created = Payment.objects.get_or_create(
                    booking=booking,
                    defaults={
                        'payment_method': 'upi',
                        'transaction_id': str(uuid.uuid4()).replace('-', '')[:16],
                        'amount': booking.total_price,
                        'payment_status': 'pending',
                        'razorpay_order_id': razorpay_order_id
                    }
                )

                if not created:
                    payment.razorpay_order_id = razorpay_order_id
                    payment.save()

                context = {
                    'booking': booking,
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'razorpay_order_id': razorpay_order_id,
                    'callback_url': request.build_absolute_uri(reverse('bookings:payment_callback')),
                    'amount': amount,
                    'currency': order_currency,
                    'email': request.user.email,
                    'phone': request.user.phone_number,
                    'name': f"{request.user.first_name} {request.user.last_name}",
                }

                return render(request, self.template_name, context)

            except Exception as e:
                messages.error(request, f'Payment gateway error: {str(e)}')
                return render(request, self.template_name, {'booking': booking, 'error': True})
        else:
        
            context = {
                'booking': booking,
                'test_mode': True,
            }
            return render(request, self.template_name, context)

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

     
        if request.POST.get('test_payment') == 'success':
         
            payment, created = Payment.objects.get_or_create(
                booking=booking,
                defaults={
                    'payment_method': 'upi',
                    'transaction_id': str(uuid.uuid4()).replace('-', '')[:16],
                    'amount': booking.total_price,
                    'payment_status': 'paid'
                }
            )

            if not created:
                payment.payment_status = 'paid'
                payment.transaction_id = str(uuid.uuid4()).replace('-', '')[:16]
                payment.save()

        
            booking.payment_status = 'paid'
            booking.is_confirmed = True
            booking.ticket_code = generate_ticket_code()
            booking.save()

            messages.success(request, 'Payment successful! Your booking is confirmed.')
            return redirect('bookings:booking_confirmation', booking_id=booking.id)
        else:
            messages.error(request, 'Payment failed. Please try again.')
            return redirect('bookings:payment', booking_id=booking.id)

@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
    """View for handling payment gateway callbacks."""
    def post(self, request):
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

           
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            try:
                client.utility.verify_payment_signature({
                    'razorpay_payment_id': payment_id,
                    'razorpay_order_id': order_id,
                    'razorpay_signature': signature
                })

                payment = Payment.objects.get(razorpay_order_id=order_id)

             
                payment.razorpay_payment_id = payment_id
                payment.razorpay_signature = signature
                payment.payment_status = 'paid'
                payment.save()

               
                booking = payment.booking
                booking.payment_status = 'paid'
                booking.is_confirmed = True
                booking.ticket_code = generate_ticket_code()
                booking.save()

           
                return redirect('bookings:booking_confirmation', booking_id=booking.id)

            except Exception as e:
              
                try:
                    payment = Payment.objects.get(razorpay_order_id=order_id)
                    payment.payment_status = 'failed'
                    payment.razorpay_payment_id = payment_id
                    payment.save()
                except Payment.DoesNotExist:
                    
                    messages.error(request, 'Payment verification failed and payment record not found.')
                    return redirect('home') 

                messages.error(request, 'Payment verification failed. Please contact support.')
                return redirect('bookings:payment', booking_id=payment.booking.id)

        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('home')

class BookingConfirmationView(LoginRequiredMixin, DetailView):
    """View for booking confirmation and ticket display."""
    model = Booking
    template_name = 'bookings/booking_confirmation.html'
    context_object_name = 'booking'
    pk_url_kwarg = 'booking_id'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.get_object()

    
        ticket_qr_data = {
            'ticket_code': booking.ticket_code,
            'event': booking.event.title,
            'date': booking.event.start_date.strftime('%d %b %Y'),
            'time': booking.event.start_time.strftime('%I:%M %p'),
            'venue': booking.event.venue.name,
        }

        if booking.seat:
            ticket_qr_data['seat'] = f"{booking.seat.row}{booking.seat.number}"
        elif booking.zone:
            ticket_qr_data['zone'] = booking.zone.name
            ticket_qr_data['quantity'] = booking.quantity

        context['ticket_qr_data'] = json.dumps(ticket_qr_data)
        return context

class UserBookingsView(LoginRequiredMixin, ListView):
    """View for displaying user's bookings."""
    model = Booking
    template_name = 'bookings/my_bookings.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-booking_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bookings = self.get_queryset()

        context['upcoming_bookings'] = bookings.filter(
            is_confirmed=True,
            is_cancelled=False,
            event__start_date__gte=timezone.now().date()
        )

        context['past_bookings'] = bookings.filter(
            is_confirmed=True,
            is_cancelled=False,
            event__end_date__lt=timezone.now().date()
        )

        context['cancelled_bookings'] = bookings.filter(is_cancelled=True)
        context['pending_bookings'] = bookings.filter(
            is_confirmed=False,
            is_cancelled=False
        )

        return context

@login_required
def download_ticket(request, booking_id):
    """View for downloading ticket as PDF."""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

   
    if not booking.is_confirmed or booking.is_cancelled:
        messages.error(request, 'Cannot download ticket for unconfirmed or cancelled booking.')
        return redirect('bookings:my_bookings')


    pdf_file = generate_pdf_ticket(booking)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.ticket_code}.pdf"'

    return response

@login_required
def cancel_booking(request, booking_id):
    """View for cancelling a booking."""
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

    if booking.is_cancelled:
        messages.error(request, 'This booking is already cancelled.')
        return redirect('bookings:my_bookings')

    if booking.event.start_date <= timezone.now().date():
        messages.error(request, 'Cannot cancel booking for an event that has already started.')
        return redirect('bookings:my_bookings')

    if request.method == 'POST':
   
        booking.is_cancelled = True
        booking.cancellation_date = timezone.now()
        booking.save()

  
        if booking.payment_status == 'paid':

            messages.success(request, 'Your booking has been cancelled. Refund will be processed within 5-7 business days.')
        else:
            messages.success(request, 'Your booking has been cancelled.')

        return redirect('bookings:my_bookings')

    return render(request, 'bookings/cancel_booking.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)



    if booking.status == 'cancelled':
        messages.error(request, "This booking has already been cancelled.")
        return redirect(reverse('bookings:my_bookings'))

    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '') 
        booking.status = 'cancelled'
        booking.cancellation_date = timezone.now()
        booking.save()
        messages.success(request, "Your booking has been cancelled successfully.")
        return redirect(reverse('bookings:my_bookings'))
    return render(request, 'bookings/cancel_booking.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    """
    View to handle booking cancellation.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '')
        booking.is_cancelled = True
        booking.cancellation_reason = cancellation_reason
        booking.cancellation_date = timezone.now()
        booking.save()
        messages.success(request, "Your booking has been cancelled.")
        return redirect('bookings:my_bookings')

    return render(request, 'bookings/cancel_booking.html', {'booking': booking})


@login_required
def event_feedback(request, event_id):
    """
    View to handle event feedback submission.
    """
    event = get_object_or_404(Event, pk=event_id)
    user = request.user

    if Feedback.objects.filter(event=event, user=user).exists():
        messages.warning(request, "You have already submitted feedback for this event.")
        return redirect('events:event_detail', event_id=event.id)  

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.event = event
            feedback.user = user
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('events:event_detail', event_id=event.id) 
        else:
            messages.error(request, "There was an error submitting your feedback. Please check the form.")
    else:
        form = FeedbackForm()
    return render(request, 'events/event_feedback.html', {'form': form, 'event': event})
