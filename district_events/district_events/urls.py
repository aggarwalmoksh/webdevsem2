from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView 
from events.views import HomeView
from django.conf import settings
from accounts.views import AboutUsView
from django.contrib.auth import views as auth_views

FLASK_CONTACT_URL = f'{settings.FLASK_SERVICE_URL}/contact/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('accounts/', include('accounts.urls')),
    path('events/', include(('events.urls', 'events'), namespace='events')),
    path('bookings/', include('bookings.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('about/', AboutUsView.as_view(), name='about_us_direct'),
    path('contact/', RedirectView.as_view(url=FLASK_CONTACT_URL, permanent=True), name='flask_contact'),
    
    # Add auth URLs (choose one option)
    path('accounts/', include('django.contrib.auth.urls')),  # Option 1
    
    # OR for Option 2:
    # path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

admin.site.site_header = 'District Events Admin'
admin.site.site_title = 'District Events Admin Portal'
admin.site.index_title = 'Welcome to District Events Admin Portal'