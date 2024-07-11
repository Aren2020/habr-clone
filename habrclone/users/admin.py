from django.contrib import admin
from .models import User, PasswordReset

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'created']

@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'token', 'created_at']