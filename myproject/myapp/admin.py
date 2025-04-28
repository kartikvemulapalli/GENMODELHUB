from django.contrib import admin
from .models import Profile  # Import your Profile model

@admin.register(Profile)  # Register the Profile model
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar')  # Customize the admin list view
    # You can add more customizations here, such as search fields, filters, etc.