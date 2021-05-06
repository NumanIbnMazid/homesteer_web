from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import Http404
from django.urls import reverse
from .models import Room, ManagerialSetting
from utils.models import Notification
from .forms import RoomCreateForm, RoomUpdateForm, ManagerialSettingForm
from accounts.utils import time_str_mix_slug
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django import forms
from memberships.models import Membership, MemberRequest
from django.http import HttpResponseRedirect
from suspicious.models import Suspicious
from tracker.models import TrackerField
from django.core.paginator import Paginator
import datetime
from django.db.models import Q

@method_decorator(login_required, name='dispatch')
class RoomCreateView(CreateView):
    template_name   = 'rooms/create.html'
    form_class      = RoomCreateForm

    def get_success_url(self):
        user    = self.request.user
        qs      = Membership.objects.filter(user=user)
        if qs.exists():
            user_instance   = Membership.objects.get(user=user)
            slug            = user_instance.room.slug
            title           = user_instance.room.title
            messages.add_message(self.request, messages.SUCCESS,
            "Room \"%s\" has been created successfully !" % title)
            return reverse('rooms:room_detail', kwargs={'slug': slug})
        return reverse('rooms:room_list')

    def form_valid(self, form):
        user                    = self.request.user
        qs                      = Room.objects.filter(creator=user)
        filter_member           = Membership.objects.filter(user=user)
        filter_request          = MemberRequest.objects.filter(user=user)
        if qs.exists():
            existed_room        = Room.objects.get(creator=user)
            form.add_error(
                None, forms.ValidationError("You already have a room named \"%s\" ! You cannot create another room with this account." % existed_room)
                )
            return super().form_invalid(form)
        elif filter_member.exists():
            existed_member      = Membership.objects.get(user=user).room.title
            form.add_error(
                None, forms.ValidationError("You are already a member of room \"%s\" ! " % existed_member)
                )
            return super().form_invalid(form)
        elif filter_request.exists():
            existed_request     = MemberRequest.objects.get(user=user).room.title
            form.add_error(
                None, forms.ValidationError("You already have a pending request for room \"%s\" ! " % existed_request)
                )
            return super().form_invalid(form)
        else:
            form.instance.creator   = user
            slug_binding            = form.instance.title.lower()+'-'+time_str_mix_slug()
            form.instance.slug      = slug_binding
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class RoomUpdateView(UpdateView):
    template_name   = 'rooms/update.html'
    form_class      = RoomUpdateForm

    def get_object(self):
        slug = self.kwargs['slug']
        room_filter = Room.objects.filter(slug=slug)
        if room_filter.exists():
            try:
                room_instance = Room.objects.get(slug=slug)
            except Room.DoesNotExist:
                raise Http404("Not found !!!")
            except Room.MultipleObjectsReturned:
                room_instance = room_filter.first()
            return room_instance
        return None

    def get_success_url(self):
        slug = self.kwargs['slug']
        messages.add_message(self.request, messages.SUCCESS, 
        "Room information updated successfully !")
        return reverse('rooms:room_detail', kwargs={'slug': slug})

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.get_object()
            return self.object.creator == request.user
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
        return super(RoomUpdateView, self).dispatch(request, *args, **kwargs)


class RoomListView(ListView):
    template_name   = 'rooms/index.html'
    paginate_by     = 12

    def get_queryset(self, *args, **kwargs):
        request = self.request
        query   = Room.objects.all().latest().active().privacy_public()
        return query

    def get_context_data(self, **kwargs):
        context             = super(RoomListView, self).get_context_data(**kwargs)
        count_rooms         = Room.objects.all().count()
        count_public_rooms  = self.object_list.count()
        count_members       = Membership.objects.all().count()
        user_instance       = self.request.user
        if user_instance.is_authenticated:
            request_filter  = MemberRequest.objects.filter(user=user_instance)
            if request_filter.exists():
                request_instance        = MemberRequest.objects.get(user=user_instance)
                request_room_instance   = request_instance.room
                request_room_slug       = request_instance.room.slug
                context['member_request']       = request_room_instance
                context['member_request_slug']  = request_room_slug
        context['total_rooms']          = count_rooms
        context['public_rooms']         = count_public_rooms
        context['total_members']        = count_members
        return context

class RoomDetailView(DetailView):
    template_name   = 'rooms/detail.html'

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        try:
            instance = Room.objects.get(slug=slug, is_active=True)
        except Room.DoesNotExist:
            raise Http404("Not Found !!!")
        except Room.MultipleObjectsReturned:
            qs = Room.objects.filter(slug=slug, is_active=True)
            instance = qs.first()
        except:
            raise Http404("Something went wrong !!!")
        return instance

    def get_context_data(self, **kwargs):
        context             = super(RoomDetailView, self).get_context_data(**kwargs)
        room_instance       = self.object.id
        room_object         = self.object
        user_instance       = self.request.user
        member_filter       = Membership.objects.filter(room_id=room_instance)
        if member_filter.exists():
            context['total_members']        = member_filter.count()
            context['members']              = member_filter
            members = Membership.objects.all()
            maintainers_filter = members.filter(
                Q(role=1) | Q(role=2),
                room_id=room_instance
            )
            context['maintainers_count'] = maintainers_filter.count()
            if self.request.user.is_authenticated:
                member_instance     = Membership.objects.filter(room_id=room_instance, user=user_instance)
                if member_instance.exists():
                    member_object   = Membership.objects.get(room_id=room_instance, user=user_instance)
                    context['member_instance']      = member_object
            cost_sector_filter = TrackerField.objects.filter(room=room_instance)
            if cost_sector_filter.count() >= 1:
                context['has_tracker'] = True
        if user_instance.is_authenticated:
            request_filter = MemberRequest.objects.filter(room_id=room_instance)
            context['member_requests_count']    = request_filter.count()
            if request_filter.exists():
                paginator2      = Paginator(request_filter, 7)
                page2           = self.request.GET.get('page')
                member_requests = paginator2.get_page(page2)
                context['member_requests'] = member_requests
            else:
                context['member_requests'] = "No requests to join"
        return context

@method_decorator(login_required, name='dispatch')
class RoomDeleteView(DeleteView):
    model           = Room
    template_name   = 'rooms/delete.html'

    def get_object(self):
        return Room.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self):
        slug = self.kwargs['slug']
        # Notification Delete
        notification_filter = Notification.objects.filter(room_identifier__iexact=slug).all()
        if notification_filter.exists():
            notification_filter.delete()
        messages.add_message(self.request, messages.SUCCESS, 
        "Room deleted successfully !")
        return reverse('rooms:room_list')

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.get_object()
            return self.object.creator == request.user
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
        return super(RoomDeleteView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ManagerialSettingUpdateView(UpdateView):
    template_name   = 'rooms/settings.html'
    form_class      = ManagerialSettingForm
    model           = ManagerialSetting

    def get_object(self):
        user = self.request.user
        room_slug           = self.request.user.membership.room.slug
        member_filter       = Membership.objects.filter(slug=user.membership.slug)
        if member_filter.exists():
            member_instance     = Membership.objects.get(slug=user.membership.slug)
            room_setting_filter = ManagerialSetting.objects.filter(room=member_instance.room)
            if room_setting_filter.exists():
                try:
                    room_setting_instance = ManagerialSetting.objects.get(room=member_instance.room)
                except ManagerialSetting.DoesNotExist:
                    raise Http404("Not Found !!!")
                except ManagerialSetting.MultipleObjectsReturned:
                    room_setting_instance = room_setting_filter.last()
                except:
                    raise Http404("Something went wrong !!!")
                return room_setting_instance
        return None

    def form_valid(self, form):
        # room_setting_instance = form.instance.shopping_type
        # pre_room_setting = self.get_object().shopping_type
        # if not pre_room_setting == room_setting_instance:
        messages.add_message(self.request, messages.SUCCESS,
        "Room Setting Updated Successfully !")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('rooms:managerial_setting')

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.get_object()
            return self.object.room.creator == request.user
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
        return super(ManagerialSettingUpdateView, self).dispatch(request, *args, **kwargs)