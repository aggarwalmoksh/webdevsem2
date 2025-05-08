import datetime
import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views import View
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
from .models import User, VerificationToken
from .forms import UserSignupForm, UserLoginForm, ProfileUpdateForm, OTPVerificationForm, ForgotPasswordForm, ResetPasswordForm
from .utils import generate_otp, send_otp_email
from django.views.decorators.http import require_POST
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model, authenticate, login  # Import get_user_model

class SignupView(View):
    """View for user registration."""
    template_name = 'accounts/signup.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserSignupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('accounts:login')

        return render(request, self.template_name, {'form': form})

    def send_verification_email(self, user):
        """Send verification email to user."""
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        expires_at = timezone.now() + datetime.timedelta(days=1)

        VerificationToken.objects.create(
            user=user,
            token=token,
            type='email_verification',
            expires_at=expires_at
        )

        verification_url = self.request.build_absolute_uri(
            reverse('accounts:verify_email', kwargs={'token': token})
        )

        send_mail(
            'Verify your District Events account',
            f'Click the link to verify your email: {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

class LoginView(View):
    form_class = UserLoginForm 
    template_name = 'accounts/login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home') 
            else:
                try:
                    UserModel = get_user_model()
                    UserModel.objects.get(username=username)
                    form.add_error('password', 'Invalid password')
                    form.cleaned_data['password'] = '' 
                except UserModel.DoesNotExist:
                    form.add_error('username', 'Invalid username')
                    form.cleaned_data['username'] = ''  
                    form.cleaned_data['password'] = ''
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """View for user logout."""
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('home')

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """View for user profile management."""
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            sensitive_fields_updated = False
            original_user = User.objects.get(pk=request.user.pk)

            if form.cleaned_data['email'] != original_user.email:
                sensitive_fields_updated = True

            if form.cleaned_data['phone_number'] != original_user.phone_number:
                sensitive_fields_updated = True

            if sensitive_fields_updated:
                otp = generate_otp()
                request.user.otp = otp
                request.user.otp_created_at = timezone.now()
                request.user.save()

                request.session['profile_form_data'] = form.cleaned_data

                send_otp_email(request.user.email, otp)

                messages.info(request, 'Please verify your identity with the OTP sent to your email.')
                return redirect('accounts:otp_verification')

            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')

        return render(request, self.template_name, {'form': form})

@method_decorator(login_required, name='dispatch')
class OTPVerificationView(View):
    """View for OTP verification."""
    template_name = 'accounts/otp_verification.html'

    def get(self, request):
        form = OTPVerificationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            stored_otp = request.user.otp

            if stored_otp and entered_otp == stored_otp:
                otp_created_at = request.user.otp_created_at
                if otp_created_at and (timezone.now() - otp_created_at).seconds < settings.OTP_EXPIRY_TIME:
                    form_data = request.session.get('profile_form_data', {})

                    for key, value in form_data.items():
                        setattr(request.user, key, value)

                    request.user.otp = None
                    request.user.otp_created_at = None
                    request.user.is_profile_complete = True
                    request.user.save()

                    if 'profile_form_data' in request.session:
                        del request.session['profile_form_data']

                    messages.success(request, 'Your profile has been updated successfully!')
                    return redirect('accounts:profile')
                else:
                    messages.error(request, 'OTP has expired. Please request a new one.')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')

        return render(request, self.template_name, {'form': form})

@method_decorator(login_required, name='dispatch')
class ResendOTPView(View):
    """View for resending OTP."""
    def get(self, request):
        otp = generate_otp()
        request.user.otp = otp
        request.user.otp_created_at = timezone.now()
        request.user.save()
        send_otp_email(request.user.email, otp)

        messages.info(request, 'A new OTP has been sent to your email.')
        return redirect('accounts:otp_verification')

class VerifyEmailView(View):
    """View for email verification."""
    def get(self, request, token):
        verification = get_object_or_404(
            VerificationToken,
            token=token,
            type='email_verification',
            is_used=False
        )

        if verification.expires_at < timezone.now():
            messages.error(request, 'Verification link has expired. Please request a new one.')
            return redirect('accounts:login')

        user = verification.user
        user.is_active = True
        user.save()

        verification.is_used = True
        verification.save()

        messages.success(request, 'Your email has been verified! You can now log in.')
        return redirect('accounts:login')

@login_required
def my_bookings(request):
    """View for displaying user's bookings."""
    from bookings.views import UserBookingsView
    return UserBookingsView.as_view()(request)

class AboutUsView(View):
    template_name = 'accounts/about_us.html'

    def get(self, request):
        context = {
            'company_name': 'District Events',
            'mission': 'Connecting people with local events.',
        }
        return render(request, self.template_name, context)



def about_us(request):
    context = {
        'company_name': 'District Events',
        'mission': 'Connecting people with local events.',
    }
    return render(request, 'accounts/about_us.html', context)


def contact_us(request):
    context = {
        'company_name': 'District Events',
        'contact': 'Chitkara University, Patiala',
    }
    return render(request, 'accounts/contact_us.html', context)



@login_required
@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email', request.user.email)
    return JsonResponse({
        'status': 'success',
        'message': 'Thank you for subscribing!'
    })

class TerminalPasswordResetView(PasswordResetView):
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

            print("\n" + "=" * 50)
            print("PASSWORD RESET LINK (COPY THIS):")
            print(reset_url)
            print("=" * 50 + "\n")

            return HttpResponseRedirect(self.get_success_url())
        except StopIteration:
            return HttpResponseRedirect(self.get_success_url())
