from django.contrib import admin
from .models import (
    Meal, 
    MealUpdateRequest, 
    TrackerField, 
    MemberTrack,
    Shopping,
    CashDepositField,
    CashDepositMember,
    TotalHolder
)

class MealAdmin(admin.ModelAdmin):
    list_display    = ['member', 'meal_today', 'meal_next_day', 'auto_entry', 'auto_entry_value', 'meal_date', 'updated_at', 'confirmed_by', 'slug', 'get_room']
    class Meta:
        model       = Meal

class MealUpdateRequestAdmin(admin.ModelAdmin):
    list_display    = ['member', 'slug', 'meal_should_be', 'request_to', 'updated_at', 'get_room']
    class Meta:
        model       = MealUpdateRequest

class TrackerFieldAdmin(admin.ModelAdmin):
    list_display    = ['title', 'room', 'slug', 'created_at', 'updated_at']
    class Meta:
        model       = TrackerField

class MemberTrackAdmin(admin.ModelAdmin):
    list_display    = ['member', 'get_room', 'tracker_field', 'cost', 'updated_at']

    # def get_tracker_field(self, obj):
    #     return "\n".join([t.tracker_field for t in obj.tracker_field.all()])

    class Meta:
        model       = MemberTrack

class ShoppingAdmin(admin.ModelAdmin):
    list_display    = ['created_by', 'item', 'slug', 'quantity', 'quantity_unit', 'cost', 'date', 'shop_type', 'get_room', 'created_at', 'updated_at']

    class Meta:
        model       = Shopping

class CashDepositFieldAdmin(admin.ModelAdmin):
    list_display    = ['title', 'slug', 'room', 'created_at', 'updated_at']
    class Meta:
        model       = CashDepositField

class CashDepositMemberAdmin(admin.ModelAdmin):
    list_display    = ['deposit_field', 'amount', 'member', 'get_room', 'created_at', 'updated_at']
    class Meta:
        model       = CashDepositMember

class TotalHolderAdmin(admin.ModelAdmin):
    list_display    = ['member', 'get_room', 'created_at', 'updated_at']
    class Meta:
        model       = TrackerField

admin.site.register(Meal, MealAdmin)
admin.site.register(MealUpdateRequest, MealUpdateRequestAdmin)
admin.site.register(TrackerField, TrackerFieldAdmin)
admin.site.register(MemberTrack, MemberTrackAdmin)
admin.site.register(Shopping, ShoppingAdmin)
admin.site.register(CashDepositField, CashDepositFieldAdmin)
admin.site.register(CashDepositMember, CashDepositMemberAdmin)
admin.site.register(TotalHolder, TotalHolderAdmin)