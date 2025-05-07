from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('seat-selection/<int:event_id>/', views.SeatSelectionView.as_view(), name='seat_selection'),
    path('payment/<int:booking_id>/', views.PaymentView.as_view(), name='payment'),
    path('payment-callback/', views.PaymentCallbackView.as_view(), name='payment_callback'),
    path('confirmation/<int:booking_id>/', views.BookingConfirmationView.as_view(), name='booking_confirmation'),
    path('my-bookings/', views.UserBookingsView.as_view(), name='my_bookings'),
    path('download-ticket/<int:booking_id>/', views.download_ticket, name='download_ticket'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('event/<int:event_id>/feedback/', views.event_feedback, name='event_feedback'),
]
