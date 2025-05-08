from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    """Extended user model with additional fields required for the application."""
    
    email = models.EmailField(unique=True)  # Ensures email uniqueness

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(13), MaxValueValidator(120)],
        blank=True, 
        null=True
    )
    is_profile_complete = models.BooleanField(default=False)

    # For OTP verification
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class VerificationToken(models.Model):
    """Model to store verification tokens for email confirmation and password reset."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64)
    type = models.CharField(max_length=20)  # 'email_verification', 'password_reset'
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.type}"

    class Meta:
        db_table = 'verification_tokens'
        verbose_name = 'Verification Token'
        verbose_name_plural = 'Verification Tokens'
