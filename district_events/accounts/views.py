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
            user.is_active = True  # Set to False if email verification is required
            user.save()

            # Optionally send verification email
            # self.send_verification_email(user)

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
    form_class = UserLoginForm  # Corrected to UserLoginForm
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
                return redirect('home')  # Adjust redirect URL as needed
            else:
                # Authentication failed, determine if it's username or password
                try:
                    UserModel = get_user_model()
                    UserModel.objects.get(username=username)
                    form.add_error('password', 'Invalid password')
                    form.cleaned_data['password'] = ''  # Clear the password
                except UserModel.DoesNotExist:
                    form.add_error('username', 'Invalid username')
                    form.cleaned_data['username'] = ''  # Clear the username
                    form.cleaned_data['password'] = ''  # Also clear password for consistency
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
            # Check if sensitive fields are being updated
            sensitive_fields_updated = False
            original_user = User.objects.get(pk=request.user.pk)

            if form.cleaned_data['email'] != original_user.email:
                sensitive_fields_updated = True

            if form.cleaned_data['phone_number'] != original_user.phone_number:
                sensitive_fields_updated = True

            if sensitive_fields_updated:
                # Generate and send OTP
                otp = generate_otp()
                request.user.otp = otp
                request.user.otp_created_at = timezone.now()
                request.user.save()

                # Store form data in session for later use
                request.session['profile_form_data'] = form.cleaned_data

                # Send OTP via email
                send_otp_email(request.user.email, otp)

                messages.info(request, 'Please verify your identity with the OTP sent to your email.')
                return redirect('accounts:otp_verification')

            # If no sensitive fields updated, save directly
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

            # Check if OTP matches and is not expired
            if stored_otp and entered_otp == stored_otp:
                otp_created_at = request.user.otp_created_at
                if otp_created_at and (timezone.now() - otp_created_at).seconds < settings.OTP_EXPIRY_TIME:
                    # OTP is valid, update user profile with session data
                    form_data = request.session.get('profile_form_data', {})

                    for key, value in form_data.items():
                        setattr(request.user, key, value)

                    # Clear OTP and session data
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

        # Send OTP via email
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

        # Check if token is expired
        if verification.expires_at < timezone.now():
            messages.error(request, 'Verification link has expired. Please request a new one.')
            return redirect('accounts:login')

        # Activate user account
        user = verification.user
        user.is_active = True
        user.save()

        # Mark token as used
        verification.is_used = True
        verification.save()

        messages.success(request, 'Your email has been verified! You can now log in.')
        return redirect('accounts:login')

@login_required
def my_bookings(request):
    """View for displaying user's bookings."""
    # This view is imported from bookings app
    from bookings.views import UserBookingsView
    return UserBookingsView.as_view()(request)

class AboutUsView(View):
    template_name = 'accounts/about_us.html'  # Create this template

    def get(self, request):
        # You can pass any relevant context data to the template here
        context = {
            'company_name': 'District Events',
            'mission': 'Connecting people with local events.',
            # Add more information as needed
        }
        return render(request, self.template_name, context)


# Alternatively, a simple function-based view:
def about_us(request):
    context = {
        'company_name': 'District Events',
        'mission': 'Connecting people with local events.',
        # Add more information as needed
    }
    return render(request, 'accounts/about_us.html', context)


class ContactUsView(View):
    """View for the Contact Us page."""
    template_name = 'accounts/contact_us.html'  # Create this template

    def get(self, request):
        from .forms import ContactForm  # Import ContactForm here to avoid circular import
        form = ContactForm()
        context = {
            'company_name': 'District Events',  #  Make sure this data is in context
            'company_address': '123 Main St',
            'company_city': 'Anytown',
            'company_state': 'CA',
            'company_zip': '12345',
            'company_country': 'USA',
            'company_email': 'info@districtevents.com',
            'company_phone': '+1 555-123-4567',
            'opening_hours': 'Mon-Fri 9am-5pm',
            'facebook_url': 'https://www.facebook.com/districtevents',
            'twitter_url': 'https://twitter.com/districtevents',
            'instagram_url': 'https://www.instagram.com/districtevents',
            'linkedin_url': 'https://www.linkedin.com/company/district-events',
            'form': form,  # Pass the form to the template
        }
        return render(request, self.template_name, context)

    def post(self, request):
        from .forms import ContactForm  # Import ContactForm here to avoid circular import
        form = ContactForm(request.POST)  # Instantiate form with POST data
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Send email (replace with your email sending logic)
            try:
                send_mail(
                    subject,
                    f"From: {name} <{email}>\n\n{message}",
                    settings.DEFAULT_FROM_EMAIL,  #  Use your setting
                    [settings.CONTACT_US_EMAIL],  #  Use a setting for recipient
                    fail_silently=False,
                )
                # Optionally, show a success message to the user (using Django messages)
                from django.contrib import messages
                messages.success(request, "Your message has been sent. We will get back to you shortly.")
                return redirect('accounts:contact_us')  #  Redirect to the contact us page
            except Exception as e:
                # Handle email sending error (log it, show error to user)
                print(f"Error sending email: {e}")
                messages.error(request, "Failed to send your message. Please try again later.")
                return render(request, self.template_name, {'form': form})  # Return the form with errors
        else:
            # If the form is invalid, re-render the template with the form and errors
            return render(request, self.template_name, {'form': form})


def contact_us(request):
    """Function-based view for the Contact Us page."""
    context = {
        'company_name': 'District Events',  #  Make sure this data is in context
        'company_address': '123 Main St',
        'company_city': 'Anytown',
        'company_state': 'CA',
        'company_zip': '12345',
        'company_country': 'USA',
        'company_email': 'info@districtevents.com',
        'company_phone': '+1 555-123-4567',
        'opening_hours': 'Mon-Fri 9am-5pm',
        'facebook_url': 'https://www.facebook.com/districtevents',
        'twitter_url': 'https://twitter.com/districtevents',
        'instagram_url': 'https://www.instagram.com/districtevents',
        'linkedin_url': 'https://www.linkedin.com/company/district-events',
    }
    return render(request, 'accounts/contact_us.html', context)


@login_required
@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email', request.user.email)
    # Here you would:
    # 1. Validate the email
    # 2. Add to your newsletter database
    # 3. Send confirmation if needed

    return JsonResponse({
        'status': 'success',
        'message': 'Thank you for subscribing!'
    })

class TerminalPasswordResetView(PasswordResetView):
    template_name = 'accounts/terminal_password_reset.html'
    email_template_name = None  # Disable email sending
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
            # Still redirect to success URL to avoid revealing account existence
            return HttpResponseRedirect(self.get_success_url())
