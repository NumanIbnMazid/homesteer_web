from django.contrib import admin
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'category', 'notify_type', 'identifier', 'room_identifier', 'slug', 'counter', 'created_at', 'updated_at']
    class Meta:
        model = Notification

admin.site.register(Notification, NotificationAdmin)
