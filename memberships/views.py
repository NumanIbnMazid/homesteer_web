from django.shortcuts import render
from .models import MemberRequest, Membership
from accounts.models import UserProfile
from tracker.models import TrackerField, MemberTrack
from utils.models import Notification
from rooms.models import Room
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from accounts.utils import time_str_mix_slug
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from .forms import MemberUpdateForm
from suspicious.models import Suspicious
import datetime
from django.db.models import Q
from django import forms

@method_decorator(login_required, name='dispatch')
class MemberUpdateView(UpdateView):
    template_name = 'membership/update.html'
    form_class      = MemberUpdateForm

    def get_object(self):
        slug = self.kwargs['slug']
        member_filter = Membership.objects.filter(slug=slug)
        if member_filter.exists():
            try:
                member_instance = Membership.objects.get(slug=slug)
            except Membership.DoesNotExist:
                raise Http404("Not found !!!")
            except Membership.MultipleObjectsReturned:
                member_instance = member_filter.first()
            return member_instance
        return None

    def get_success_url(self):
        slug = self.request.user.membership.room.slug
        member_instance = self.object.user.profile.get_username()
        messages.add_message(self.request, messages.SUCCESS, 
        "%s\'s Membership updated successfully !" %member_instance)
        return reverse('rooms:room_detail', kwargs={'slug': slug})

    def form_valid(self, form):
        role_instance   = form.instance.role
        pre_role        = self.get_object().role
        if pre_role != 1 and pre_role != 2:
            if role_instance == 1 or role_instance == 2:
                room_instance = self.request.user.membership.room
                members = Membership.objects.all()
                maintainers_count = members.filter(
                    Q(role=1) | Q(role=2),
                    room = room_instance
                ).count()
                if maintainers_count >= 6:
                    form.add_error(
                        None, forms.ValidationError("Your room has already 6 maintainers. You cannot assign more !")
                    )
                    return super().form_invalid(form)
        return super().form_valid(form)

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.get_object()
            if self.object.room == request.user.membership.room:
                if request.user.membership.role == 2 :
                    return True
        return False

    def dispatch(self, request, *args, **kwargs):
        instance_user   = self.request.user
        if not self.user_passes_test(request):
            suspicious_user = Suspicious.objects.filter(user=instance_user)
            if suspicious_user.exists():
                suspicious_user_instance    = Suspicious.objects.get(user=instance_user)
                current_attempt             = suspicious_user_instance.attempt
                total_attempt               = current_attempt + 1
                update_time                 = datetime.datetime.now()
                suspicious_user.update(attempt=total_attempt, last_attempt=update_time)
            else:
                Suspicious.objects.get_or_create(user=instance_user)
            messages.add_message(self.request, messages.ERROR, 
                "You are not allowed. Your account is being tracked for suspicious activity !"
            )
            return HttpResponseRedirect(reverse('home'))
        return super(MemberUpdateView, self).dispatch(request, *args, **kwargs)

@login_required
def member_request_create(request, slug):
    if request.user.is_authenticated:
        user_instance   = request.user
        room_instance   = Room.objects.get(slug=slug)
        count_members   = Membership.objects.filter(room=room_instance).count()
        url             = reverse('rooms:room_list')
        filter_request  = MemberRequest.objects.filter(user=user_instance)
        filter_member   = Membership.objects.filter(user=user_instance)
        if count_members > 14:
            messages.add_message(request, messages.WARNING,
            "There are no slot to join this room ! Maximum 15 members can join per room.")
        elif filter_request.exists():
            existed_request = MemberRequest.objects.get(user=user_instance).room.title
            messages.add_message(request, messages.WARNING,
            "You already have a pending request for room \"%s\" !" % existed_request)
        elif filter_member.exists():
            existed_member  = Membership.objects.get(user=user_instance).room.title
            messages.add_message(request, messages.WARNING,
            "You are already a member of room \"%s\" !" % existed_member)
        else:
            slug_binding    = user_instance.username.lower()+'-'+time_str_mix_slug()
            MemberRequest.objects.get_or_create(user=user_instance, room=room_instance, slug=slug_binding)
            # ----------- Notification Starts -----------
            notify_type = "join_room"
            if UserProfile.objects.filter(user=user_instance).exists():
                notify_user_instance = UserProfile.objects.get(user=user_instance)
                notify_slug = notify_user_instance.user.username.lower()+'-'+time_str_mix_slug()
                notification_filter = Notification.objects.filter(sender=notify_user_instance,receiver=notify_user_instance, notify_type__iexact="join_room")
                if notification_filter.exists():
                    counter = notification_filter.first().counter + 1
                    notification_filter.update(
                        counter = counter,
                        updated_at = datetime.datetime.now()
                    )
                else:
                    Notification.objects.create(
                        sender=notify_user_instance,
                        receiver=notify_user_instance,
                        slug=notify_slug,
                        notify_type=notify_type,
                        room_identifier=slug,
                        counter=1
                    )
            # ----------- Notification Ends -----------
            messages.add_message(request, messages.SUCCESS,
            "Your request sent successfully !")
            return HttpResponseRedirect(url)
    return HttpResponseRedirect(reverse('rooms:room_list'))

@login_required
def member_request_confirm(request, slug):
    url = reverse('home')
    if request.user.is_authenticated:
        user_filter    = MemberRequest.objects.filter(slug=slug)
        
        if user_filter.exists():
            member_instance = MemberRequest.objects.get(slug=slug)
            user_instance   = member_instance.user
            room_instance   = member_instance.room
            count_members   = Membership.objects.filter(room=room_instance).count()
            if count_members > 14:
                messages.add_message(request, messages.WARNING,
                "There are no slot to join this room ! Maximum 15 members can join per room.")
                url = reverse('rooms:room_detail', kwargs={'slug': room_instance.slug})
            else:
                slug_binding    = user_instance.username.lower()+'-'+time_str_mix_slug()
                Membership.objects.get_or_create(user=user_instance, room=room_instance, slug=slug_binding)
                membership_check = Membership.objects.filter(user=user_instance)
                if membership_check.exists():
                    url = reverse('rooms:room_detail', kwargs={'slug': room_instance.slug})
                    created_filter  = MemberRequest.objects.filter(user=user_instance)
                    if created_filter.exists():
                        created_filter.delete()
                    tracker_filter = TrackerField.objects.filter(room=room_instance)
                    if tracker_filter.exists():
                        member_track_filter = MemberTrack.objects.filter(member__user=user_instance)
                        if not member_track_filter.exists():
                            for field in tracker_filter:
                                MemberTrack.objects.create(
                                    member=membership_check.first(),
                                    tracker_field=field,
                                    cost=0.00
                                )
                    # ----------- Notification Deletion Starts -----------
                    notify_type = "join_room"
                    notify_user = member_instance.user
                    if UserProfile.objects.filter(user=notify_user).exists():
                        notify_user_instance = UserProfile.objects.get(user=notify_user)
                        notification_filter = Notification.objects.filter(receiver=notify_user_instance, notify_type__iexact="join_room")
                        if notification_filter.exists():
                            notification_filter.delete()
                    # ----------- Notification Deletion Ends -----------
                    messages.add_message(request, messages.SUCCESS,
                    "\'%s\' is now member of your room !" %user_instance.username)
                    return HttpResponseRedirect(url)
    return HttpResponseRedirect(url)

@login_required
def member_request_delete(request, slug):
    url = reverse('home')
    if request.user.is_authenticated:
        request_filter      = MemberRequest.objects.filter(slug=slug)
        if request_filter.exists():
            user_instance = request_filter.first().user
            request_filter.delete()
            url             = request.META.get('HTTP_REFERER', '/')
            # ----------- Notification Deletion Starts -----------
            notify_type = "join_room"
            if UserProfile.objects.filter(user=user_instance).exists():
                notify_user_instance = UserProfile.objects.get(user=user_instance)
                notification_filter = Notification.objects.filter(receiver=notify_user_instance, notify_type__iexact="join_room")
                if notification_filter.exists():
                    notification_filter.delete()
            # ----------- Notification Deletion Ends -----------
            messages.add_message(request, messages.SUCCESS,
            "Member request deleted successfully !")
            return HttpResponseRedirect(url)
    return HttpResponseRedirect(url)

@login_required
def member_request_delete_all(request, slug):
    url = reverse('home')
    if request.user.is_authenticated:
        room_filter      = Room.objects.filter(slug=slug)
        if room_filter.exists():
            room_instance = Room.objects.get(slug=slug)
            requests_filter = MemberRequest.objects.filter(room=room_instance).all()
            # Notification Delete Starts
            if requests_filter.exists():
                for requests in requests_filter:
                    user_filter = UserProfile.objects.filter(user=requests.user)
                    if requests_filter.exists():
                        for user in user_filter:
                            deletion_filter = Notification.objects.filter(receiver=user)
                            if requests_filter.exists():
                                deletion_filter.delete()
                # Notification Delete Ends
                # Requests Delete Starts
                requests_filter.delete()
                # Requests Delete Ends
                url             = request.META.get('HTTP_REFERER', '/')
                messages.add_message(request, messages.SUCCESS,
                "All member requests deleted successfully !")
                return HttpResponseRedirect(url)
    return HttpResponseRedirect(url)

@login_required
def member_delete(request, slug):
    url = reverse('home')
    if request.user.is_authenticated:
        member_filter       = Membership.objects.filter(slug=slug)
        if member_filter.exists():
            member_filter.delete()
            # url             = request.META.get('HTTP_REFERER', '/')
            messages.add_message(request, messages.SUCCESS,
            "Membership removed successfully !")
            return HttpResponseRedirect(url)
    return HttpResponseRedirect(url)