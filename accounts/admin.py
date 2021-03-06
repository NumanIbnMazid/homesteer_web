from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

UserAdmin.list_display += ('is_active',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'slug', 'gender','updated_at']
    class Meta:
        model = UserProfile

admin.site.register(UserProfile, UserProfileAdmin)
