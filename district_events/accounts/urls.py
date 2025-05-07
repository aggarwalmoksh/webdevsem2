from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('otp-verification/', views.OTPVerificationView.as_view(), name='otp_verification'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend_otp'),
    path('verify-email/<str:token>/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('about/', views.AboutUsView.as_view(), name='about_us'),
    path('contact-us/', views.ContactUsView.as_view(), name='contact_us_direct'),
    path('contact/', views.contact_us, name='contact_us'),
]
