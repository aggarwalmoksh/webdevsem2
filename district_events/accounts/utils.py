import random
import string
from django.core.mail import send_mail
from django.conf import settings

def generate_otp(length=6):
    """Generate a random OTP."""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(to_email, otp):
    """Send OTP to user's email."""
    subject = 'District Events - Verification Code'
    message = f'Your verification code is: {otp}\nThis code will expire in 5 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [to_email]
    
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    
    return True

def validate_otp(user, otp):
    """
    Validate OTP for a user.
    Returns True if OTP is valid, False otherwise.
    """
    from django.utils import timezone
    if not user.otp or user.otp != otp:
        return False
    
    # Check if OTP is expired (5 minutes)
    otp_created_at = user.otp_created_at
    if not otp_created_at:
        return False
    
    time_difference = (timezone.now() - otp_created_at).seconds
    if time_difference > settings.OTP_EXPIRY_TIME:
        return False
    
    return True
