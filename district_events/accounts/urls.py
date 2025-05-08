from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.http import HttpResponseRedirect

app_name = 'accounts'

class TerminalPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/terminal_password_reset.html'
    email_template_name = None
    subject_template_name = None
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = form.get_users(email).__next__()
            token = self.token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{settings.SITE_URL}/accounts/reset/{uid}/{token}/"
            
            print("\n" + "="*50)
            print("PASSWORD RESET LINK (COPY THIS):")
            print(reset_url)
            print("="*50 + "\n")
            
            return HttpResponseRedirect(self.get_success_url())
        except StopIteration:
            return HttpResponseRedirect(self.get_success_url())

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
    
        response['Refresh'] = '5; url=/accounts/login/'
        return response

urlpatterns = [

    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
   path('forgot-password/', 
    TerminalPasswordResetView.as_view(), 
    name='forgot_password'), 
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_sent.html'
        ), 
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/accounts/reset/done/'
        ), 
        name='password_reset_confirm'),
    path('reset/done/', 
        CustomPasswordResetCompleteView.as_view(), 
        name='password_reset_complete'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('otp-verification/', views.OTPVerificationView.as_view(), name='otp_verification'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend_otp'),
    path('verify-email/<str:token>/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('about/', views.AboutUsView.as_view(), name='about_us'),
    path('contact-us/', views.ContactUsView.as_view(), name='contact_us_direct'),
    path('contact/', views.contact_us, name='contact_us'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]