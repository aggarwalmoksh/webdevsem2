from django.urls import path
from . import views 
from django.contrib.auth.decorators import login_required

app_name = 'events' 

urlpatterns = [
    path('', views.home_view, name='home'),
    path('list/', views.EventListView.as_view(), name='event_list'),
    path('detail/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('api/seats/<int:event_id>/', views.get_seats_json, name='get_seats_json'),
    path('api/filter-by-city/', views.filter_events_by_city, name='filter_events_by_city'),
    path('about/', views.about_view, name='about'),
    path('test-filter/', views.test_filter_view, name='test_filter'),
    path('contact/', views.contact_view, name='contact'),
    path('feedback/', login_required(views.feedback_view), name='feedback'),
    path('feedback/submit/', login_required(views.feedback_submit), name='feedback_submit'),
    path('event_feedback/<int:event_id>/', login_required(views.event_feedback), name='event_feedback'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms/', views.terms_view, name='terms'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/<int:order_id>/', views.order_summary_view, name='order_summary'),
]