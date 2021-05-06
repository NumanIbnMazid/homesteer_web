from django.contrib import admin
from .models import Membership, MemberRequest

class MembershipAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'role', 'room', 'slug', 'created_at', 'updated_at']
    class Meta:
        model = Membership

class MemberRequestAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'room', 'slug', 'created_at', 'updated_at']
    class Meta:
        model = MemberRequest

admin.site.register(Membership, MembershipAdmin)
admin.site.register(MemberRequest, MemberRequestAdmin)