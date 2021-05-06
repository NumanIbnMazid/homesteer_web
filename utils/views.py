from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from utils.models import Notification
from django.views.generic import ListView
from accounts.models import UserProfile

@login_required
def notification_delete(request, slug):
    url = reverse('home')
    notification_filter = Notification.objects.filter(slug=slug)
    if notification_filter.exists():
        notification_filter.delete()
    if request.user.membership:
        slug = request.user.membership.room.slug
        # url = reverse('rooms:room_detail', kwargs={'slug': slug})
        url = reverse('utils:notification_list')
    return HttpResponseRedirect(url)

class NotificationListView(ListView):
    template_name       = 'notifications/list.html'
    paginate_by         = 4
    model               = Notification
    # context_object_name = 'objects'

    def get_queryset(self, *args, **kwargs):
        request = self.request
        user_profile = UserProfile.objects.filter(user=request.user)
        if user_profile.exists():
            user_instance = UserProfile.objects.get(user=request.user)
            query   = Notification.objects.filter(receiver=user_instance).order_by('-updated_at')
        return query

