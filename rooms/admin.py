from django.contrib import admin
from .models import Room, ManagerialSetting

class RoomAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug', 'is_active', 'privacy', 'creator', 'updated_at']
    class Meta:
        model = Room

class ManagerialSettingAdmin(admin.ModelAdmin):
    list_display    = ['room', 'shopping_type', 'is_CUD_able', 'created_at', 'updated_at']

    class Meta:
        model       = ManagerialSetting

admin.site.register(Room, RoomAdmin)
admin.site.register(ManagerialSetting, ManagerialSettingAdmin)
