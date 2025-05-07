from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, VerificationToken

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom User model."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'age', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    list_filter = ('is_staff', 'is_active', 'is_profile_complete')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'age')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Profile', {'fields': ('is_profile_complete',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'age'),
        }),
    )

@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    """Admin interface for VerificationToken model."""
    list_display = ('user', 'type', 'created_at', 'expires_at', 'is_used')
    list_filter = ('type', 'is_used')
    search_fields = ('user__username', 'user__email', 'token')
    readonly_fields = ('token', 'created_at')
