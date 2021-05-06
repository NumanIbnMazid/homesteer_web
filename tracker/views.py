from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django import forms
from .models import (
    TrackerField, 
    MemberTrack, 
    Meal, 
    MealUpdateRequest,
    Shopping,
    CashDepositField,
    CashDepositMember,
    TotalHolder
)
from rooms.models import ManagerialSetting
from memberships.models import Membership
from suspicious.models import Suspicious
from accounts.models import UserProfile
from utils.models import Notification
from .forms import (
    TrackerFieldCreateForm, 
    AssignFieldToMemberForm, 
    TrackerFieldUpdateForm,
    MealEntryForm,
    MealUpdateForm,
    MealUpdateAdminForm,
    MealUpdateRequestForm,
    MealUpdateRequestConfirmForm,
    ShoppingCreateForm,
    ShoppingUpdateForm,
    CashDepositFieldCreateForm,
    AssignCashDepositToMemberForm
)
from django.urls import reverse
from django.contrib import messages
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView
)
from django.http import HttpResponseRedirect, Http404
from accounts.utils import time_str_mix_slug
from django.core.paginator import Paginator
import datetime
from django.db.models import Q, F, Sum
import time
import calendar


@method_decorator(login_required, name='dispatch')
class TrackerCreateView(CreateView):
    template_name   = 'tracker/create.html'
    form_class      = TrackerFieldCreateForm

    def get_success_url(self):
        return reverse('tracker:tracker_create')

    def get_form_kwargs(self):
        kwargs = super(TrackerCreateView, self).get_form_kwargs()
        if self.form_class:
            kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(TrackerCreateView, self).get_context_data(**kwargs)
        room_instance   = self.request.user.membership.room
        tracker_fields  = TrackerField.objects.all()
        field_filter    = tracker_fields.filter(room=room_instance)
        if field_filter.exists():
            context['cost_sectors'] = field_filter
        return context

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.request.user.membership
            room_slug = self.object.room.slug
            member_filter = Membership.objects.filter(user=request.user, room__slug=room_slug)
            if member_filter.exists():
                member_instance = Membership.objects.get(user=request.user, room__slug=room_slug)
                if member_instance.role == 2 or self.object.room.creator == request.user:
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
        return super(TrackerCreateView, self).dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class TrackerUpdateView(UpdateView):
    template_name   = 'tracker/update.html'
    form_class      = TrackerFieldUpdateForm

    def get_object(self):
        return TrackerField.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        room_instance       = self.request.user.membership.room
        title               = form.instance.title
        title_safe          = form.initial['title']
        title_filter        = TrackerField.objects.filter(title__iexact=title, room=room_instance).exclude(title__iexact=title_safe)
        if title_filter.exists():
            title_instance  = TrackerField.objects.get(title__iexact=title, room=room_instance)
            form.add_error(
                'title', forms.ValidationError("\"%s\" Field is already exists ! Please try another one." % title_instance)
                )
            return super().form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        slug = self.request.user.membership.room.slug
        messages.add_message(self.request, messages.SUCCESS, 
        "\"%s\" information updated successfully !" % self.object)
        return reverse('tracker:tracker_create')

    def get_context_data(self, **kwargs):
        context = super(TrackerUpdateView, self).get_context_data(**kwargs)
        room_instance   = self.request.user.membership.room
        tracker_fields  = TrackerField.objects.all()
        field_filter    = tracker_fields.filter(room=room_instance)
        if field_filter.exists():
            context['cost_sectors'] = field_filter
        return context

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.get_object()
            room_slug = self.object.room.slug
            member_filter = Membership.objects.filter(user=request.user, room__slug=room_slug)
            if member_filter.exists():
                member_instance = Membership.objects.get(user=request.user, room__slug=room_slug)
                if member_instance.role == 2 or self.object.room.creator == request.user:
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
        return super(TrackerUpdateView, self).dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class TrackerDeleteView(DeleteView):
    model = TrackerField
    template_name   = 'tracker/delete.html'

    def get_object(self):
        return TrackerField.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "\"%s\" deleted successfully !" % self.object
        )
        return reverse('tracker:tracker_create')

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.get_object()
            room_slug = self.object.room.slug
            member_filter = Membership.objects.filter(user=request.user, room__slug=room_slug)
            if member_filter.exists():
                member_instance = Membership.objects.get(user=request.user, room__slug=room_slug)
                if member_instance.role == 2 or self.object.room.creator == request.user:
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
        return super(TrackerDeleteView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class AssignFieldToMemberView(CreateView):
    template_name   = 'tracker/assign/assign_field_to_member.html'
    form_class      = AssignFieldToMemberForm
    
    def get_success_url(self):
        if self.request.user.membership:
            url = reverse('tracker:cost_chart')
        else:
            url = reverse('home')
        return url

    def get_form_kwargs(self):
        kwargs = super(AssignFieldToMemberView, self).get_form_kwargs()
        if self.form_class:
            kwargs.update({'request': self.request})
        if kwargs['instance'] is None:
            kwargs['slug'] = self.kwargs['slug']
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AssignFieldToMemberView, self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        room_instance = self.request.user.membership.room
        member_filter   = Membership.objects.filter(slug=slug)
        cost_sectors    = TrackerField.objects.all()
        cost_sector_filter = cost_sectors.filter(room=room_instance)
        if member_filter.exists():
            member_instance = Membership.objects.get(slug=slug).user.profile.get_smallname
        else:
            member_instance = "Member"
        context["member"] = member_instance
        if cost_sector_filter.exists():
            context['cost_sector_exists'] = True
        
        return context

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.membership = request.user.membership
            room_slug = self.membership.room.slug
            member_filter = Membership.objects.filter(user=request.user, room__slug=room_slug)
            if member_filter.exists():
                member_instance = Membership.objects.get(user=request.user, room__slug=room_slug)
                if member_instance.role == 2 or self.membership.room.creator == request.user:
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
        return super(AssignFieldToMemberView, self).dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class MealCreateView(CreateView):
    template_name   = 'tracker/meal/create.html'
    form_class      = MealEntryForm

    def form_valid(self, form):
        if not time.strftime("%H-%M") == "00-00":
            slug            = self.request.user.membership.slug
            now             = datetime.datetime.now()
            next_day        = (datetime.date.today() + datetime.timedelta(days=1))
            tomorrow        = next_day.strftime("%Y-%m-%d")
            meal_today      = form.cleaned_data.get('meal_today')
            meal_next_day   = form.cleaned_data.get('meal_next_day')
            auto_entry_value= form.cleaned_data.get('auto_entry_value')
            if auto_entry_value == None or auto_entry_value == "" :
                auto_entry  = False
            else:
                auto_entry  = True
            # Auto Entry Defination Starts
            day_range           = calendar.monthrange(now.year, now.month)[1]
            now_day_binding     = int(now.day) + 2
            auto_day_binding    = int(day_range) - 1
            if now.day >= auto_day_binding and auto_entry == True:
                auto_entry          = False
                auto_entry_value    = None
                messages.add_message(self.request, messages.WARNING,
                "Auto entry is not workable in last two days of month! Please change it from next month.")
            if not now.day >= auto_day_binding and not auto_entry == False:
                day_binding         = now_day_binding
                start_date          = datetime.date(now.year, now.month, day_binding)
                end_date            = datetime.date(now.year, now.month, day_range)
                def daterange(start_date, end_date):
                    for n in range(int ((end_date - start_date).days) + 1):
                        yield start_date + datetime.timedelta(n)
            # Auto Entry Defination Ends
            member_filter   = Membership.objects.filter(slug=slug).only('user')
            if member_filter.exists():
                member_instance = Membership.objects.get(slug=slug)
                existed_meal_filter = Meal.objects.filter(
                            Q(meal_date__day=now.day, meal_date__month=now.month, meal_date__year=now.year),
                            member=member_instance
                            ).only('member', 'meal_date')
                if existed_meal_filter.exists():
                    messages.add_message(self.request, messages.WARNING,
                                    "You already have a meal entry for today. Please update it !")
                else:
                    slug_binding = member_instance.user.username.lower()+'-'+str(now.day)+'-'+time_str_mix_slug()
                    form.instance.member            = member_instance
                    form.instance.meal_today        = meal_today
                    form.instance.meal_next_day     = meal_next_day
                    form.instance.auto_entry        = auto_entry
                    form.instance.auto_entry_value  = auto_entry_value
                    form.instance.meal_date         = now
                    form.instance.confirmed_by      = member_instance
                    form.instance.slug              = slug_binding
                    slug_binding = member_instance.user.username.lower()+'-'+next_day.strftime("%d")+'-'+time_str_mix_slug()
                    Meal.objects.get_or_create(
                        member              = member_instance,
                        meal_today          = meal_next_day,
                        meal_next_day       = 0,
                        auto_entry          = auto_entry,
                        auto_entry_value    = auto_entry_value,
                        meal_date           = tomorrow,
                        slug                = slug_binding,
                        confirmed_by        = member_instance
                    )
                    if auto_entry == True:
                        for single_date in daterange(start_date, end_date):
                            slug_binding = member_instance.user.username.lower()+'-'+str(single_date.strftime("%d"))+'-'+time_str_mix_slug()
                            Meal.objects.get_or_create(
                                member              = member_instance,
                                meal_today          = auto_entry_value,
                                meal_next_day       = auto_entry_value,
                                auto_entry          = auto_entry,
                                auto_entry_value    = auto_entry_value,
                                meal_date           = single_date,
                                slug                = slug_binding,
                                confirmed_by        = member_instance
                            )
                    if len(existed_meal_filter) >= 2:
                        existed_meal_filter.first().delete()
                    messages.add_message(self.request, messages.SUCCESS,
                                        "Meal information added successfully !")
                    return super().form_valid(form)
            else:
                instance_user   = self.request.user
                suspicious_user = Suspicious.objects.filter(user=instance_user).only('user')
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
        else:
            form.add_error(
                None, forms.ValidationError("Regular maintenance break ! Please try again 1 minute later.")
                )
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        response    = super(MealCreateView, self).post(request, *args, **kwargs)
        user        = self.request.user
        now         = datetime.datetime.now()
        day_range   = calendar.monthrange(now.year, now.month)[1]
        members_filter = Membership.objects.filter(room=user.membership.room).only('room')
        if members_filter.exists():
            members_instance = Membership.objects.get(room=user.membership.room, user=user)
            for member in members_filter:
                start_date          = datetime.date(now.year, now.month, 1)
                end_date            = datetime.date(now.year, now.month, day_range)
                def daterange(start_date, end_date):
                    for n in range(int ((end_date - start_date).days) + 1):
                        yield start_date + datetime.timedelta(n)
                for single_date in daterange(start_date, end_date):
                    members_meal_filter = Meal.objects.filter(
                        member=member, meal_date__day=single_date.day, meal_date__month=single_date.month, meal_date__year=single_date.year
                    ).only('member', 'meal_date')
                    if not members_meal_filter.exists():
                        slug_binding = member.user.username.lower()+'-'+single_date.strftime("%d")+'-'+time_str_mix_slug()
                        Meal.objects.get_or_create(
                            member=member,
                            slug=slug_binding,
                            meal_today=None,
                            meal_next_day=None,
                            auto_entry=False,
                            auto_entry_value=None,
                            meal_date=single_date,
                            confirmed_by=member
                        )
        return response

    def get_success_url(self):
        member_slug     = self.request.user.membership.slug
        now             = datetime.datetime.now()
        member_filter   = Membership.objects.filter(slug = member_slug).only('user')
        if member_filter.exists():
            member_instance = Membership.objects.get(slug=member_slug)
            meal_filter     = Meal.objects.filter(
                Q(meal_date__day=now.day, meal_date__month=now.month, meal_date__year=now.year),
                member=member_instance
            ).only('member', 'meal_date')
            if meal_filter.exists():
                meal_instance = meal_filter.last()
                slug = meal_instance.slug
            else:
                slug = None
        return reverse('tracker:meal_update', kwargs={'slug': slug})

    def get_context_data(self, **kwargs):
        context = super(MealCreateView, self).get_context_data(**kwargs)
        member_slug     = self.request.user.membership.slug
        now             = datetime.datetime.now()
        day_range       = calendar.monthrange(now.year, now.month)[1]
        if now.day < day_range:
            day_to_view = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d")
        else:
            day_to_view = now.day
        member_filter   = Membership.objects.filter(slug=member_slug).only('user')
        if member_filter.exists():
            member_instance     = Membership.objects.get(slug=member_slug)
            context['member']   = member_instance.user.profile.get_smallname
            context['time']     = datetime.date.today()
            meals               = Meal.objects.all()
            member_meal_filter  = Meal.objects.filter(
                                    Q(meal_date__day__lte=day_to_view, meal_date__month=now.month, meal_date__year=now.year),
                                    member=member_instance
                                    ).only('member', 'meal_date').order_by('-meal_date')
            if member_meal_filter.exists():
                paginator       = Paginator(member_meal_filter, 7)
                page            = self.request.GET.get('page')
                member_meals    = paginator.get_page(page)
                context['member_meals'] = member_meals
                context['count']        = member_meal_filter.count()
            total_filter = TotalHolder.objects.filter(
                member=member_instance
            )
            if total_filter.exists():
                context['total'] = total_filter.first()
        return context

@method_decorator(login_required, name='dispatch')
class MealUpdateView(UpdateView):
    template_name   = 'tracker/meal/update.html'
    form_class      = MealUpdateForm

    def get_object(self):
        slug            = self.request.user.membership.slug
        now             = datetime.datetime.now()
        member_filter   = Membership.objects.filter(slug=slug).only('user')
        if member_filter.exists():
            member_instance     = Membership.objects.get(slug=slug)
            meals               = Meal.objects.all()
            existed_meal_filter = Meal.objects.filter(
                            Q(meal_date__day=now.day, meal_date__month=now.month, meal_date__year=now.year),
                            member=member_instance
                            ).only('member', 'meal_date')
            if existed_meal_filter.exists():
                existed_meal_check = Meal.objects.filter(
                            Q(meal_date__day=now.day, meal_date__month=now.month, meal_date__year=now.year),
                            member=member_instance
                            ).last()
                return existed_meal_check
        return None

    def get_form_kwargs(self):
        kwargs = super(MealUpdateView, self).get_form_kwargs()
        if self.form_class:
            kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        if not time.strftime("%H-%M") == "00-00":
            member_slug     = self.request.user.membership.slug
            now             = datetime.datetime.now()
            next_day        = (datetime.date.today() + datetime.timedelta(days=1))
            meal_next_day   = form.cleaned_data.get('meal_next_day')
            auto_entry_value= form.cleaned_data.get('auto_entry_value')
            if auto_entry_value == None:
                auto_entry  = False
            else:
                auto_entry  = True
            # Auto Entry Defination Starts
            day_range           = calendar.monthrange(now.year, now.month)[1]
            now_day_binding     = int(now.day) + 2
            auto_day_binding    = int(day_range) - 1
            if now.day >= auto_day_binding and auto_entry == True:
                auto_entry          = False
                auto_entry_value    = None
                messages.add_message(self.request, messages.WARNING,
                "Auto entry is not workable in last two days of month! Please change it from next month.")
            if not now.day >= auto_day_binding and not auto_entry == False:
                day_binding         = now_day_binding
                start_date          = datetime.date(now.year, now.month, day_binding)
                end_date            = datetime.date(now.year, now.month, day_range)
                def daterange(start_date, end_date):
                    for n in range(int ((end_date - start_date).days) + 1):
                        yield start_date + datetime.timedelta(n)
            # Auto Entry Defination Ends
            member_filter = Membership.objects.filter(slug=member_slug).only('user')
            if member_filter.exists():
                member_instance = Membership.objects.get(slug=member_slug)
                meal_filter_datetime = Meal.objects.filter(
                    Q(meal_date__day=now.day, meal_date__month=now.month, meal_date__year=now.year),
                    member=member_instance
                    ).only('member', 'meal_date')
                if meal_filter_datetime.exists():
                    meal_filter_slug = meal_filter_datetime.last().slug
                    meal_filter = Meal.objects.filter(slug=meal_filter_slug)
                    if meal_filter.exists():
                        member_meal                     = Meal.objects.filter(member=member_instance).only('member', 'meal_date')
                        form.instance.auto_entry        = auto_entry
                        form.instance.auto_entry_value  = auto_entry_value
                        tomorrow_meal           = member_meal.filter(
                            Q(meal_date__day=next_day.day, meal_date__month=next_day.month, meal_date__year=next_day.year)
                        ).only('meal_date')
                        if tomorrow_meal.exists():
                            tomorrow_meal.update(
                                meal_today          = meal_next_day,
                                meal_next_day       = 0,
                                auto_entry          = auto_entry,
                                auto_entry_value    = auto_entry_value,
                                confirmed_by        = member_instance
                            )
                        else:
                            slug_binding = member_instance.user.username.lower()+'-'+next_day.strftime("%d")+'-'+time_str_mix_slug()
                            Meal.objects.create(
                                member              = member_instance,
                                meal_today          = meal_next_day,
                                meal_next_day       = 0,
                                auto_entry          = auto_entry,
                                auto_entry_value    = auto_entry_value,
                                meal_date           = next_day,
                                slug                = slug_binding,
                                confirmed_by        = member_instance
                            )
                        if len(tomorrow_meal) >= 2:
                            tomorrow_meal.first().delete()
                        if auto_entry == False:
                            if not now.day == day_range:
                                deletion_day = int(next_day.day) + 1
                                auto_meals   = member_meal.filter(
                                    Q(meal_date__day__gte=deletion_day, meal_date__month=now.month, meal_date__year=now.year)
                                ).only('meal_date')
                                if auto_meals.exists():
                                    if now.day >= auto_day_binding:
                                        auto_meals.exclude(meal_date__day=day_range).update(
                                            meal_today=None,
                                            meal_next_day=None,
                                            auto_entry=False,
                                            auto_entry_value=None,
                                        )
                                    else:
                                        auto_meals.update(
                                            meal_today=None,
                                            meal_next_day=None,
                                            auto_entry=False,
                                            auto_entry_value=None,
                                        )
                        if auto_entry == True:
                            for single_date in daterange(start_date, end_date):
                                slug_binding = member_instance.user.username.lower()+'-'+str(single_date.strftime("%d"))+'-'+time_str_mix_slug()
                                auto_meals   = member_meal.filter(
                                    Q(meal_date__day=single_date.day, meal_date__month=single_date.month, meal_date__year=single_date.year),
                                ).only('meal_date')
                                if auto_meals.exists():
                                    auto_meals.update(
                                        meal_today          = auto_entry_value,
                                        meal_next_day       = auto_entry_value,
                                        auto_entry          = auto_entry,
                                        auto_entry_value    = auto_entry_value,
                                        confirmed_by        = member_instance
                                    )
                                else:
                                    Meal.objects.create(
                                        member              = member_instance,
                                        meal_today          = auto_entry_value,
                                        meal_next_day       = auto_entry_value,
                                        auto_entry          = auto_entry,
                                        auto_entry_value    = auto_entry_value,
                                        meal_date           = single_date,
                                        slug                = slug_binding,
                                        confirmed_by        = member_instance
                                    )
                            if len(auto_meals) >= 2:
                                auto_meals.first().delete()
                        messages.add_message(self.request, messages.SUCCESS,
                            "Meal information updated successfully !"
                        )
                        return super().form_valid(form)
                else:
                    form.add_error(
                        None, forms.ValidationError("You don't have any meal entry for today to update! Please Entry first.")
                    )
            else:
                instance_user   = self.request.user
                suspicious_user = Suspicious.objects.filter(user=instance_user).only('user')
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
        else:
            form.add_error(
                None, forms.ValidationError("Regular maintenance break ! Please try again 1 minute later.")
            )
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        response = super(MealUpdateView, self).post(request, *args, **kwargs)
        user = self.request.user
        now  = datetime.datetime.now()
        next_day  = (datetime.date.today() + datetime.timedelta(days=1))
        day_range = calendar.monthrange(now.year, now.month)[1]
        members_filter = Membership.objects.filter(room=user.membership.room).only('user', 'room')
        if members_filter.exists():
            for member in members_filter:
                if now.day == day_range:
                    next_month_range    = calendar.monthrange(next_day.year, next_day.month)[1]
                    start_date          = datetime.date(next_day.year, next_day.month, 1)
                    end_date            = datetime.date(next_day.year, next_day.month, next_month_range)
                    def daterange(start_date, end_date):
                        for n in range(int ((end_date - start_date).days) + 1):
                            yield start_date + datetime.timedelta(n)
                    for single_date in daterange(start_date, end_date):
                        members_meal_filter = Meal.objects.filter(
                            member=member, meal_date__day=single_date.day, meal_date__month=single_date.month, meal_date__year=single_date.year
                        ).only('member', 'meal_date')
                        if not members_meal_filter.exists():
                            slug_binding = member.user.username.lower()+'-'+single_date.strftime("%d")+'-'+time_str_mix_slug()
                            Meal.objects.get_or_create(
                                member=member,
                                slug=slug_binding,
                                meal_today=None,
                                meal_next_day=None,
                                auto_entry=False,
                                auto_entry_value=None,
                                meal_date=single_date,
                                confirmed_by=member
                            )
        return response

    def get_success_url(self):
        slug            = self.kwargs['slug']
        return reverse('tracker:meal_update', kwargs={'slug': slug})

    def get_context_data(self, **kwargs):
        context = super(MealUpdateView, self).get_context_data(**kwargs)
        member_slug     = self.request.user.membership.slug
        now             = datetime.datetime.now()
        day_range       = calendar.monthrange(now.year, now.month)[1]
        tomorrow        = (datetime.date.today() + datetime.timedelta(days=1))
        if now.day < day_range:
            day_to_view = tomorrow.day
        else:
            day_to_view = now.day
        member_filter   = Membership.objects.filter(slug=member_slug).only('user')
        if member_filter.exists():
            member_instance     = Membership.objects.get(slug=member_slug)
            context['member']   = member_instance.user.profile.get_smallname
            context['time']     = datetime.date.today()
            meals               = Meal.objects.all()
            member_meal_filter  = Meal.objects.filter(
                                    Q(meal_date__day__lte=day_to_view, meal_date__month=now.month, meal_date__year=now.year),
                                    member=member_instance
                                    ).only('member', 'meal_date').order_by('-meal_date')
            if member_meal_filter.exists():
                context['last_meal'] = member_meal_filter.first()
                paginator       = Paginator(member_meal_filter, 7)
                page            = self.request.GET.get('page')
                member_meals    = paginator.get_page(page)
                context['member_meals'] = member_meals
                context['count']        = member_meal_filter.count()
            if now.day == day_range:
                tomorrow_meal_filter    = Meal.objects.filter(
                                        Q(meal_date__day=tomorrow.day, meal_date__month=tomorrow.month, meal_date__year=tomorrow.year),
                                        member=member_instance
                                        ).only('member', 'meal_date').order_by('-meal_date')
                context['tomorrow_meal'] = tomorrow_meal_filter.last()
            requested_meal_filter = MealUpdateRequest.objects.filter(
                member=member_instance, member__room=member_instance.room
            ).only('member')
            if requested_meal_filter.exists():
                meal_filter = Meal.objects.filter(
                    member=member_instance, member__room=member_instance.room
                ).only('member')
                if meal_filter.exists():
                    context['meals'] = meal_filter
                context['requested_meals'] = requested_meal_filter
            total_filter = TotalHolder.objects.filter(
                member=member_instance
            )
            if total_filter.exists():
                context['total'] = total_filter.first()
        return context


@method_decorator(login_required, name='dispatch')
class MealUpdateAdminView(UpdateView):
    template_name   = 'tracker/meal/update-admin.html'
    form_class      = MealUpdateAdminForm

    def get_object(self):
        user            = self.request.user
        slug            = self.kwargs['slug']
        meal_filter     = Meal.objects.filter(slug=slug)
        if meal_filter.exists():
            meal_instance = meal_filter.first()
            return meal_instance
        return None

    def form_valid(self, form):
        if not time.strftime("%H-%M") == "00-00":
            member_slug     = self.request.user.membership.slug
            member_filter = Membership.objects.filter(slug=member_slug).only('user')
            if member_filter.exists():
                member_instance = Membership.objects.get(slug=member_slug)
                form.instance.confirmed_by = member_instance
                messages.add_message(self.request, messages.SUCCESS,
                    "Meal information updated successfully !"
                )
                # ----------- Notification Creation Starts -----------
                user = self.request.user
                object = self.get_object()
                if UserProfile.objects.filter(user=user).exists():
                    notify_sender_instance      = UserProfile.objects.get(user=user)
                    if UserProfile.objects.filter(user=object.member.user).exists():
                        notify_receiver_instance    = UserProfile.objects.get(user=object.member.user)
                        notify_type = "meal_update_by_maintainer"
                        room_slug   = user.membership.room.slug
                        meal_notify_instance = Meal.objects.filter(slug=object.slug).last()
                        notify_slug = notify_receiver_instance.user.username.lower()+'-'+time_str_mix_slug()
                        notification_filter = Notification.objects.filter(identifier__iexact=object.slug,sender=notify_sender_instance, receiver=notify_receiver_instance, notify_type__iexact="meal_update_by_maintainer")
                        if notification_filter.exists():
                            counter = notification_filter.first().counter + 1
                            notification_filter.update(
                                counter = counter,
                                updated_at = datetime.datetime.now(),
                                message="updated your meal of %s and changed it to %s." %(meal_notify_instance.meal_date.strftime("%B-%d-%Y"), form.instance.meal_today)
                            )
                        else:
                            Notification.objects.create(
                                sender=notify_sender_instance,
                                receiver=notify_receiver_instance,
                                slug=notify_slug,
                                category="message",
                                notify_type=notify_type,
                                identifier=object.slug,
                                room_identifier=room_slug,
                                counter=1,
                                message="updated your meal of %s and changed it to %s." %(meal_notify_instance.meal_date.strftime("%B-%d-%Y"), form.instance.meal_today)
                            )
                # ----------- Notification Creation Ends -----------
                return super().form_valid(form)
        else:
            form.add_error(
                None, forms.ValidationError("Regular maintenance break ! Please try again 1 minute later.")
            )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('tracker:meal_chart')

    def post(self, request, *args, **kwargs):
        response = super(MealUpdateAdminView, self).post(request, *args, **kwargs)
        user = self.request.user
        now  = datetime.datetime.now()
        next_day  = (datetime.date.today() + datetime.timedelta(days=1))
        day_range = calendar.monthrange(now.year, now.month)[1]
        user_member_filter = Membership.objects.filter(user=user)
        if user_member_filter.exists():
            user_membership = user_member_filter.first()
        members_filter = Membership.objects.filter(room=user.membership.room).only('user', 'room')
        if members_filter.exists():
            for member in members_filter:
                if now.day == day_range:
                    next_month_range    = calendar.monthrange(next_day.year, next_day.month)[1]
                    start_date          = datetime.date(next_day.year, next_day.month, 1)
                    end_date            = datetime.date(next_day.year, next_day.month, next_month_range)
                    def daterange(start_date, end_date):
                        for n in range(int ((end_date - start_date).days) + 1):
                            yield start_date + datetime.timedelta(n)
                    for single_date in daterange(start_date, end_date):
                        members_meal_filter = Meal.objects.filter(
                            member=member, meal_date__day=single_date.day, meal_date__month=single_date.month, meal_date__year=single_date.year
                        ).only('member', 'meal_date')
                        if not members_meal_filter.exists():
                            slug_binding = member.user.username.lower()+'-'+single_date.strftime("%d")+'-'+time_str_mix_slug()
                            Meal.objects.get_or_create(
                                member=member,
                                slug=slug_binding,
                                meal_today=None,
                                meal_next_day=None,
                                auto_entry=False,
                                auto_entry_value=None,
                                meal_date=single_date,
                                confirmed_by=user_membership
                            )
                if now.day < day_range:
                    start_date          = datetime.date(next_day.year, next_day.month, 1)
                    end_date            = datetime.date(next_day.year, next_day.month, day_range)
                    def daterange(start_date, end_date):
                        for n in range(int ((end_date - start_date).days) + 1):
                            yield start_date + datetime.timedelta(n)
                    for single_date in daterange(start_date, end_date):
                        members_meal_filter = Meal.objects.filter(
                            member=member, meal_date__day=single_date.day, meal_date__month=single_date.month, meal_date__year=single_date.year
                        ).only('member', 'meal_date')
                        if not members_meal_filter.exists():
                            slug_binding = member.user.username.lower()+'-'+single_date.strftime("%d")+'-'+time_str_mix_slug()
                            Meal.objects.get_or_create(
                                member=member,
                                slug=slug_binding,
                                meal_today=None,
                                meal_next_day=None,
                                auto_entry=False,
                                auto_entry_value=None,
                                meal_date=single_date,
                                confirmed_by=user_membership
                            )
        return response

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            now  = datetime.datetime.now()
            self.object = self.get_object()
            if self.object.member.room == request.user.membership.room and request.user.membership.role == 2:
                if self.object.meal_date.strftime("%d-%m-%Y") == now.strftime("%d-%m-%Y") and not self.object.member == request.user.membership:
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
        return super(MealUpdateAdminView, self).dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class MealUpdateRequestView(CreateView):
    template_name   = 'tracker/meal/update-request.html'
    form_class      = MealUpdateRequestForm

    def get_form_kwargs(self):
        kwargs = super(MealUpdateRequestView, self).get_form_kwargs()
        if self.form_class:
            kwargs.update({'request': self.request})
            kwargs.update({'slug': self.kwargs['slug']})
        return kwargs

    def get_object(self):
        slug = self.kwargs['slug']
        meal_filter = Meal.objects.filter(slug=slug).only('slug')
        if meal_filter.exists():
            try:
                meal_instance = Meal.objects.get(slug=slug)
            except Meal.DoesNotExist:
                raise Http404("Not Found !!!")
            except Meal.MultipleObjectsReturned:
                meal_instance = meal_filter.last()
            except:
                raise Http404("Something went wrong !!!")
        else:
            meal_instance = None
        return meal_instance

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.get_object()
            return self.object.member.user == request.user
        return False

    def dispatch(self, request, *args, **kwargs):
        instance_user   = self.request.user
        if not self.user_passes_test(request):
            suspicious_user = Suspicious.objects.filter(user=instance_user).only('user')
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
        return super(MealUpdateRequestView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        meal_slug       = self.kwargs['slug']
        member          = self.request.user
        meal_should_be  = form.cleaned_data.get('meal_should_be')
        request_to      = form.cleaned_data.get('request_to')
        if (Membership.objects.filter(user=member)).exists():
            member_instance = Membership.objects.get(user=member)
            meal_filter     = MealUpdateRequest.objects.filter(slug=meal_slug)
            if meal_filter.exists():
                meal_filter.delete()
            form.instance.member = member_instance
            form.instance.slug   = meal_slug
            # ----------- Notification Starts -----------
            notify_type = "meal_update"
            meal_date_filter = Meal.objects.filter(slug=meal_slug)
            if meal_date_filter.exists():
                identifier = meal_slug
                notify_sender_instance      = UserProfile.objects.get(user__username=member)
                notify_receiver_instance    = UserProfile.objects.get(user__username=request_to)
                notify_slug = notify_receiver_instance.user.username.lower()+'-'+time_str_mix_slug()
                notification_filter = Notification.objects.filter(sender=notify_sender_instance, notify_type__iexact="meal_update", identifier__iexact=identifier)
                if notification_filter.exists():
                    counter = notification_filter.first().counter + 1
                    notification_filter.update(
                        receiver = notify_receiver_instance,
                        counter = counter,
                        updated_at = datetime.datetime.now()
                    )
                else:
                    Notification.objects.create(
                        sender=notify_sender_instance,
                        receiver=notify_receiver_instance,
                        slug=notify_slug,
                        notify_type=notify_type,
                        identifier=identifier,
                        room_identifier=member.membership.room.slug,
                        counter=1
                    )
                # ----------- Notification Ends -----------
                messages.add_message(self.request, messages.SUCCESS,
                "Your request created successfully and is under review")
                return super().form_valid(form)
        messages.add_message(self.request, messages.WARNING,
        "Something went wrong !")
        return super().form_invalid(form)

    def get_success_url(self):
        member     = self.request.user
        now             = datetime.datetime.now()
        if Membership.objects.filter(user=member).exists():
            member_instance = Membership.objects.get(user=member)
            meal_filter     = Meal.objects.filter(
                Q(meal_date__day=now.day, meal_date__month=now.month, meal_date__year=now.year),
                member=member_instance
            )
            if meal_filter.exists():
                meal_instance = meal_filter.last()
                slug = meal_instance.slug
                return reverse('tracker:meal_update', kwargs={'slug': slug})
            else:
                return reverse('home')
        return reverse('home')

    def get_context_data(self, **kwargs):
        context = super(MealUpdateRequestView, self).get_context_data(**kwargs)
        slug            = self.kwargs['slug']
        member_slug     = self.request.user.membership.slug
        now             = datetime.datetime.now()
        day_range       = calendar.monthrange(now.year, now.month)[1]
        if now.day < day_range:
            day_to_view = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d")
        else:
            day_to_view = now.day
        member_filter   = Membership.objects.filter(slug=member_slug)
        if member_filter.exists():
            member_instance     = Membership.objects.get(slug=member_slug)
            context['member']   = member_instance.user.profile.get_smallname
            context['time']     = datetime.date.today()
            # meals               = Meal.objects.all()
            member_meal_filter  = Meal.objects.filter(
                                    Q(meal_date__day__lte=day_to_view, meal_date__month=now.month, meal_date__year=now.year),
                                    member=member_instance
                                    ).order_by('-meal_date')
            if member_meal_filter.exists():
                paginator       = Paginator(member_meal_filter, 7)
                page            = self.request.GET.get('page')
                member_meals    = paginator.get_page(page)
                context['member_meals'] = member_meals
                context['count']        = member_meal_filter.count()
            meal_filter         = Meal.objects.filter(slug=slug, member=member_instance)
            if meal_filter.exists():
                context['requested_meal'] = Meal.objects.filter(slug=slug, member=member_instance).last()
        return context


@login_required
def meal_update_request_cancel(request, slug):
    url     = reverse('home')
    user    = request.user
    if user.membership:
        member_filter = Membership.objects.filter(user=user, room=user.membership.room)
        if member_filter.exists():
            member_instance = Membership.objects.get(user=user, room=user.membership.room)
            room = member_instance.room
            room_slug = room.slug
            meal_request_filter = MealUpdateRequest.objects.filter(
                member=member_instance, slug=slug
            )
            if meal_request_filter.exists():
                meal_instance = MealUpdateRequest.objects.get(
                    member=member_instance, slug=slug
                )
            security_cross_check = Membership.objects.filter(
                user=user, room=meal_instance.member.room
            )
            if security_cross_check.exists():
                second_security_layer = MealUpdateRequest.objects.filter(
                    member=member_instance, slug=slug, member__room=meal_instance.member.room
                )
                if second_security_layer.exists():
                    meal_request_filter.delete()
                    messages.add_message(request, messages.SUCCESS,
                    "Meal Update Request cancelled successfully !")
                    url = request.META.get('HTTP_REFERER', '/')
                    # ----------- Notification Starts -----------
                    notify_type = "meal_update"
                    meal_date_filter = Meal.objects.filter(slug=slug)
                    if meal_date_filter.exists():
                        identifier = slug
                        notify_sender_instance      = UserProfile.objects.get(user__username=user)
                        notify_receiver_instance    = UserProfile.objects.get(user__username=meal_instance.request_to)
                        notification_filter = Notification.objects.filter(
                            sender=notify_sender_instance, notify_type__iexact="meal_update", identifier__iexact=identifier, room_identifier=member_instance.room.slug
                        )
                        if notification_filter.exists():
                            notification_filter.delete()
                        # ----------- Notification Ends -----------
            else:
                suspicious_user = Suspicious.objects.filter(user=user)
                if suspicious_user.exists():
                    suspicious_user_instance    = Suspicious.objects.get(user=user)
                    current_attempt             = suspicious_user_instance.attempt
                    total_attempt               = current_attempt + 1
                    update_time                 = datetime.datetime.now()
                    suspicious_user.update(attempt=total_attempt, last_attempt=update_time)
                else:
                    Suspicious.objects.get_or_create(user=user)
                messages.add_message(request, messages.ERROR, 
                    "You are not allowed. Your account is being tracked for suspicious activity !"
                )
    else:   
        messages.add_message(request, messages.WARNING,
        "Something went wrong !")
    return HttpResponseRedirect(url)


@method_decorator(login_required, name='dispatch')
class MealUpdateRequestConfirmView(UpdateView):
    template_name   = 'tracker/meal/update-request-confirm.html'
    form_class      = MealUpdateRequestConfirmForm

    def get_object(self):
        slug = self.kwargs['slug']
        meal_filter = Meal.objects.filter(slug=slug)
        if Membership.objects.filter(user=self.request.user).exists():
            member = Membership.objects.get(user=self.request.user)
            meal_request_filter = MealUpdateRequest.objects.filter(slug=slug, request_to=member)
            if meal_request_filter.exists():
                if meal_filter.exists():
                    try:
                        meal_instance = Meal.objects.get(slug=slug)
                        return meal_instance
                    except Meal.DoesNotExist:
                        raise Http404("Not Found !!!")
                    except Meal.MultipleObjectsReturned:
                        meal_instance = meal_filter.first()
                    except:
                        raise Http404("Something went wrong !!!")
                else:
                    notification = Notification.objects.filter(identifier=slug,notify_type__iexact="meal_update")
                    if notification.exists():
                        notification.delete()
        return None

    def get_form_kwargs(self):
        kwargs = super(MealUpdateRequestConfirmView, self).get_form_kwargs()
        if self.form_class:
            kwargs.update({'request': self.request})
            kwargs.update({'slug': self.kwargs['slug']})
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        slug = self.kwargs['slug']
        if Membership.objects.filter(slug=user.membership.slug).exists():
            member_instance     = Membership.objects.get(slug=user.membership.slug)
            request_filter = MealUpdateRequest.objects.filter(slug=slug, request_to=member_instance)
            if request_filter.exists():
                request_instance = request_filter.last()
                meal_today = request_instance.meal_should_be
                form.instance.meal_today    = meal_today
                form.instance.confirmed_by  = member_instance
                request_filter.delete()
                # ----------- Notification Creation Starts -----------
                if UserProfile.objects.filter(user=user).exists():
                    notify_sender_instance      = UserProfile.objects.get(user=user)
                    if UserProfile.objects.filter(user=request_instance.member.user).exists():
                        notify_receiver_instance    = UserProfile.objects.get(user=request_instance.member.user)
                        notification = Notification.objects.filter(identifier__iexact=slug, sender=notify_receiver_instance, receiver=notify_sender_instance, notify_type__iexact="meal_update")
                        if notification.exists():
                            notification.delete()
                        notify_type = "meal_update_confirmed"
                        room_slug   = user.membership.room.slug
                        meal_notify_instance = Meal.objects.filter(slug=slug).last()
                        notify_slug = notify_receiver_instance.user.username.lower()+'-'+time_str_mix_slug()
                        notification_filter = Notification.objects.filter(identifier__iexact=slug,sender=notify_sender_instance, receiver=notify_receiver_instance, notify_type__iexact="meal_update_confirmed")
                        if notification_filter.exists():
                            counter = notification_filter.first().counter + 1
                            notification_filter.update(
                                counter = counter,
                                updated_at = datetime.datetime.now()
                            )
                        else:
                            Notification.objects.create(
                                sender=notify_sender_instance,
                                receiver=notify_receiver_instance,
                                slug=notify_slug,
                                category="message",
                                notify_type=notify_type,
                                identifier=slug,
                                room_identifier=room_slug,
                                counter=1,
                                message="confirmed your request to update meal of %s and changed it to %s." %(meal_notify_instance.meal_date.strftime("%B-%d-%Y"), meal_today)
                            )
                # ----------- Notification Creation Ends -----------
                messages.add_message(self.request, messages.SUCCESS,
                    "Meal updated successfully !"
                )
                return super().form_valid(form)
            else:
                messages.add_message(self.request, messages.WARNING,
                    "Content Expired !!!"
                )
        else:
            instance_user   = user
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
        messages.add_message(self.request, messages.WARNING,
            "Something went wrong !"
        )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('utils:notification_list')

    def get_context_data(self, **kwargs):
        context = super(MealUpdateRequestConfirmView, self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        if Meal.objects.filter(slug=slug).exists():
            meal_instance = Meal.objects.filter(slug=slug).last()
            if MealUpdateRequest.objects.filter(slug=slug).exists():
                meal_request_instance = MealUpdateRequest.objects.filter(slug=slug).last()
                context["meal"] = meal_instance
                context["meal_request"] = meal_request_instance
        return context

@login_required
def meal_update_request_deny(request, slug):
    url     = reverse('home')
    user    = request.user
    room_slug    = request.user.membership.room.slug
    meal_request_filter = MealUpdateRequest.objects.filter(slug=slug)
    if meal_request_filter.exists():
        meal_request_notify_instance = meal_request_filter.last()
        meal_instance = Meal.objects.filter(slug=slug).last()
        meal_request_filter.delete()
        url = reverse('utils:notification_list')
        if UserProfile.objects.filter(user=user).exists():
            notify_sender_instance      = UserProfile.objects.get(user=user)
            if UserProfile.objects.filter(user=meal_request_notify_instance.member.user).exists():
                notify_receiver_instance    = UserProfile.objects.get(user=meal_request_notify_instance.member.user)
                notification = Notification.objects.filter(identifier__iexact=slug, sender=notify_receiver_instance, receiver=notify_sender_instance, notify_type__iexact="meal_update")
                if notification.exists():
                    notification.delete()
                notify_type = "meal_request_cancel"
                notify_slug = notify_receiver_instance.user.username.lower()+'-'+time_str_mix_slug()
                notification_filter = Notification.objects.filter(identifier__iexact=slug, sender=notify_sender_instance, receiver=notify_receiver_instance, notify_type__iexact="meal_request_cancel")
                if notification_filter.exists():
                    counter = notification_filter.first().counter + 1
                    notification_filter.update(
                        counter = counter,
                        updated_at = datetime.datetime.now()
                    )
                else:
                    Notification.objects.create(
                        sender=notify_sender_instance,
                        receiver=notify_receiver_instance,
                        slug=notify_slug,
                        category="message",
                        notify_type=notify_type,
                        identifier=slug,
                        room_identifier=room_slug,
                        counter=1,
                        message="rejected your request to update meal of %s" %(meal_instance.meal_date.strftime("%B-%d-%Y"))
                    )
            messages.add_message(request, messages.SUCCESS,
            "Request cancelled successfully !")
            return HttpResponseRedirect(url)
    messages.add_message(request, messages.WARNING,
    "Something went wrong !")
    return HttpResponseRedirect(url)


@method_decorator(login_required, name='dispatch')
class ShoppingCreateView(CreateView):
    template_name   = 'tracker/shopping/create.html'
    form_class      = ShoppingCreateForm

    def form_valid(self, form):
        user = self.request.user
        membership_filter = Membership.objects.filter(user=user, room=user.membership.room)
        if membership_filter.exists():
            member_instance = Membership.objects.get(user=user, room=user.membership.room)
            item = form.instance.item
            quantity_unit = form.instance.quantity_unit
            slug_binding                = item.lower()+'-'+'reg-'+time_str_mix_slug()
            form.instance.slug          = slug_binding
            form.instance.created_by    = member_instance
            form.instance.shop_type     = 0
            if not quantity_unit == None:
                form.instance.quantity_unit = quantity_unit.lower()
            messages.add_message(self.request, messages.SUCCESS,
            "\"%s\" inserted successfully to your shopping list!" %item)
            return super().form_valid(form)
        messages.add_message(self.request, messages.SUCCESS,
        "Something went wrong!!!")
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(ShoppingCreateView, self).get_form_kwargs()
        if self.form_class:
            kwargs.update({'request': self.request})
        return kwargs
    
    def get_success_url(self):
        return reverse('tracker:shopping_create')

    def get_context_data(self, **kwargs):
        context = super(ShoppingCreateView, self).get_context_data(**kwargs)
        user = self.request.user
        member_filter = Membership.objects.filter(
            user=user, room=user.membership.room
        )
        if member_filter.exists():
            now             = datetime.datetime.now()
            member_instance = member_filter.first()
            shopping_filter = Shopping.objects.filter(
                created_by=member_instance, shop_type=0, created_by__room=member_instance.room, date__month=now.month, date__year=now.year
            ).order_by('-created_at')
            if shopping_filter.exists():
                paginator               = Paginator(shopping_filter, 7)
                page                    = self.request.GET.get('page')
                paginated_shoppings     = paginator.get_page(page)
                context['shoppings']    = paginated_shoppings
                context['count']        = shopping_filter.count()
            total_filter = TotalHolder.objects.filter(
                member=member_instance
            )
            if total_filter.exists():
                context['total'] = total_filter.first()
            context['time'] = now
        return context

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.member = self.request.user.membership
            room_slug = self.member.room.slug
            member_filter = Membership.objects.filter(user=request.user, room__slug=room_slug).only('user', 'room')
            if member_filter.exists():
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
        return super(ShoppingCreateView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class MonthlyShoppingCreateView(CreateView):
    template_name   = 'tracker/shopping/create.html'
    form_class      = ShoppingCreateForm

    def form_valid(self, form):
        user = self.request.user
        membership_filter = Membership.objects.filter(user=user, room=user.membership.room)
        if membership_filter.exists():
            member_instance = Membership.objects.get(user=user, room=user.membership.room)
            item                        = form.instance.item
            quantity_unit               = form.instance.quantity_unit
            slug_binding                = item.lower()+'-'+'mon-'+time_str_mix_slug()
            form.instance.slug          = slug_binding
            form.instance.shop_type     = 1
            form.instance.created_by    = member_instance
            if not quantity_unit == None:
                form.instance.quantity_unit = quantity_unit.lower()
            messages.add_message(self.request, messages.SUCCESS,
            "\"%s\" inserted successfully to your room's monthly shopping list!" %item)
            return super().form_valid(form)
        messages.add_message(self.request, messages.SUCCESS,
        "Something went wrong !!! Please try agin later !")
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(MonthlyShoppingCreateView, self).get_form_kwargs()
        if self.form_class:
            kwargs.update({'request': self.request})
        return kwargs
    
    def get_success_url(self):
        return reverse('tracker:monthly_shopping_create')

    def get_context_data(self, **kwargs):
        context = super(MonthlyShoppingCreateView, self).get_context_data(**kwargs)
        user = self.request.user
        member_filter = Membership.objects.filter(
            user=user, room=user.membership.room
        )
        if member_filter.exists():
            now             = datetime.datetime.now()
            member_instance = member_filter.first()
            shopping_filter = Shopping.objects.filter(
                created_by__room=member_instance.room, shop_type=1, date__month=now.month, date__year=now.year
            ).order_by('-created_at')
            if shopping_filter.exists():
                paginator               = Paginator(shopping_filter, 7)
                page                    = self.request.GET.get('page')
                paginated_shoppings     = paginator.get_page(page)
                context['shoppings']    = paginated_shoppings
                context['count']        = shopping_filter.count()
            total_filter = TotalHolder.objects.filter(
                member=member_instance
            )
            if total_filter.exists():
                context['total'] = total_filter.first()
            context['time'] = now
        return context

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.member = self.request.user.membership
            room_slug = self.member.room.slug
            member_filter = Membership.objects.filter(user=request.user, room__slug=room_slug)
            if member_filter.exists():
                member_instance = member_filter.first()
                if member_instance.role == 2:
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
        return super(MonthlyShoppingCreateView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ShoppingUpdateView(UpdateView):
    template_name   = 'tracker/shopping/update.html'
    form_class      = ShoppingUpdateForm

    def get_object(self):
        slug = self.kwargs['slug']
        shopping_filter = Shopping.objects.filter(slug=slug)
        if shopping_filter.exists():
            try:
                shopping_instance = Shopping.objects.get(slug=slug)
            except Shopping.DoesNotExist:
                raise Http404("Not found !!!")
            except Shopping.MultipleObjectsReturned:
                shopping_instance = shopping_filter.first()
            return shopping_instance
        return None

    def get_form_kwargs(self):
        kwargs = super(ShoppingUpdateView, self).get_form_kwargs()
        if self.form_class:
            kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        membership_filter = Membership.objects.filter(user=user, room=user.membership.room)
        if membership_filter.exists():
            item = form.instance.item
            quantity_unit = form.instance.quantity_unit
            if not quantity_unit == None:
                form.instance.quantity_unit = quantity_unit.lower()
            messages.add_message(self.request, messages.SUCCESS,
            "\"%s\" updated successfully!" %item)
            return super().form_valid(form)
        messages.add_message(self.request, messages.WARNING,
        "Something went wrong !!!")
        return super().form_invalid(form)
        
    def get_success_url(self):
        return reverse('tracker:shopping_create')

    def get_context_data(self, **kwargs):
        context = super(ShoppingUpdateView, self).get_context_data(**kwargs)
        user = self.request.user
        member_filter = Membership.objects.filter(
            user=user, room=user.membership.room
        )
        if member_filter.exists():
            now             = datetime.datetime.now()
            member_instance = member_filter.first()
            shopping_filter = Shopping.objects.filter(
                created_by=member_instance, shop_type=0, created_by__room=member_instance.room, date__month=now.month, date__year=now.year
            ).order_by('-created_at')
            if shopping_filter.exists():
                paginator       = Paginator(shopping_filter, 7)
                page            = self.request.GET.get('page')
                paginated_shoppings     = paginator.get_page(page)
                context['shoppings']    = paginated_shoppings
                context['count']        = shopping_filter.count()
            total_filter = TotalHolder.objects.filter(
                member=member_instance
            )
            if total_filter.exists():
                context['total'] = total_filter.first()
            context['time'] = now
        return context

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.get_object()
            member_filter = Membership.objects.filter(user=request.user)
            if member_filter.exists():
                member_instance = member_filter.first()
                return self.object.created_by == member_instance
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
        return super(ShoppingUpdateView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class MonthlyShoppingUpdateView(UpdateView):
    template_name   = 'tracker/shopping/update.html'
    form_class      = ShoppingUpdateForm

    def get_object(self):
        slug = self.kwargs['slug']
        shopping_filter = Shopping.objects.filter(slug=slug)
        if shopping_filter.exists():
            try:
                shopping_instance = Shopping.objects.get(slug=slug)
            except Shopping.DoesNotExist:
                raise Http404("Not found !!!")
            except Shopping.MultipleObjectsReturned:
                shopping_instance = shopping_filter.first()
            return shopping_instance
        return None

    def get_form_kwargs(self):
        kwargs = super(MonthlyShoppingUpdateView, self).get_form_kwargs()
        if self.form_class:
            kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        membership_filter = Membership.objects.filter(user=user, room=user.membership.room)
        if membership_filter.exists():
            item = form.instance.item
            quantity_unit = form.instance.quantity_unit
            if not quantity_unit == None:
                form.instance.quantity_unit = quantity_unit.lower()
            messages.add_message(self.request, messages.SUCCESS,
            "\"%s\" updated successfully!" %item)
            return super().form_valid(form)
        messages.add_message(self.request, messages.WARNING,
        "Something went wrong !!!")
        return super().form_invalid(form)
        
    def get_success_url(self):
        return reverse('tracker:monthly_shopping_create')

    def get_context_data(self, **kwargs):
        context = super(MonthlyShoppingUpdateView, self).get_context_data(**kwargs)
        user = self.request.user
        member_filter = Membership.objects.filter(
            user=user, room=user.membership.room
        )
        if member_filter.exists():
            now             = datetime.datetime.now()
            member_instance = member_filter.first()
            shopping_filter = Shopping.objects.filter(
                shop_type=1, created_by__room=member_instance.room, date__month=now.month, date__year=now.year
            ).order_by('-created_at')
            if shopping_filter.exists():
                paginator               = Paginator(shopping_filter, 7)
                page                    = self.request.GET.get('page')
                paginated_shoppings     = paginator.get_page(page)
                context['shoppings']    = paginated_shoppings
                context['count']        = shopping_filter.count()
            total_filter = TotalHolder.objects.filter(
                member=member_instance
            )
            if total_filter.exists():
                context['total'] = total_filter.first()
            context['time'] = now
        return context

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.get_object()
            member_filter = Membership.objects.filter(user=request.user)
            if member_filter.exists():
                member_instance = member_filter.first()
                if self.object.created_by.room == member_instance.room and member_instance.role == 2:
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
        return super(MonthlyShoppingUpdateView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ShoppingDeleteView(DeleteView):
    model           = Shopping
    template_name   = 'tracker/shopping/delete.html'

    def get_object(self):
        slug = self.kwargs['slug']
        shopping_filter = Shopping.objects.filter(slug=slug)
        if shopping_filter.exists():
            shopping_instance = shopping_filter.first()
            return shopping_instance
        return None

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "\"%s\" deleted successfully !" % self.object
        )
        return reverse('tracker:shopping_create')

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.get_object()
            room_slug = self.object.created_by.room.slug
            member_filter = Membership.objects.filter(user=request.user, room__slug=room_slug)
            if member_filter.exists():
                return self.object.created_by.user == request.user
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
        return super(ShoppingDeleteView, self).dispatch(request, *args, **kwargs)



@method_decorator(login_required, name='dispatch')
class MonthlyShoppingDeleteView(DeleteView):
    model           = Shopping
    template_name   = 'tracker/shopping/delete.html'

    def get_object(self):
        slug = self.kwargs['slug']
        shopping_filter = Shopping.objects.filter(slug=slug)
        if shopping_filter.exists():
            shopping_instance = shopping_filter.first()
            return shopping_instance
        return None

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "\"%s\" deleted successfully !" % self.object
        )
        return reverse('tracker:monthly_shopping_create')

    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.get_object()
            room_slug = self.object.created_by.room.slug
            member_filter = Membership.objects.filter(user=request.user, room__slug=room_slug)
            if member_filter.exists():
                if self.object.created_by.room == request.user.membership.room and request.user.membership.role ==2:
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
        return super(MonthlyShoppingDeleteView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class CashDepositFieldCreateView(CreateView):
    template_name   = 'tracker/deposit/create.html'
    form_class      = CashDepositFieldCreateForm

    def form_valid(self, form):
        room_instance       = self.request.user.membership.room
        title               = form.instance.title
        if not title == None :
            title_filter        = CashDepositField.objects.filter(title__iexact=title, room=room_instance)
            if title_filter.exists():
                form.add_error(
                    'title', forms.ValidationError("\"%s\" is already exists ! Please try another one." % title)
                )
            else:
                slug_binding        = title.lower()+'-'+time_str_mix_slug()
                form.instance.room  = room_instance
                form.instance.slug  = slug_binding
                messages.add_message(self.request, messages.SUCCESS, 
                "Cash Deposit Field \"%s\" created successfully !" %title)
                return super().form_valid(form)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('tracker:deposit_field_create')

    def get_context_data(self, **kwargs):
        context = super(CashDepositFieldCreateView, self).get_context_data(**kwargs)
        room_instance       = self.request.user.membership.room
        deposit_fields_filter           = CashDepositField.objects.filter(room=room_instance)
        if deposit_fields_filter.exists():
            context['deposit_fields']   = deposit_fields_filter
        return context

    def user_passes_test(self, request):
        user = request.user
        if user.membership:
            if user.membership.role == 2:
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
        return super(CashDepositFieldCreateView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class CashDepositFieldUpdateView(UpdateView):
    template_name   = 'tracker/deposit/update.html'
    form_class      = CashDepositFieldCreateForm

    def get_object(self):
        slug = self.kwargs['slug']
        field_filter = CashDepositField.objects.filter(slug=slug)
        if field_filter.exists():
            return field_filter.first()
        return None

    def form_valid(self, form):
        room_instance       = self.request.user.membership.room
        title               = form.instance.title
        title_safe          = form.initial['title']
        title_filter        = CashDepositField.objects.filter(title__iexact=title, room=room_instance).exclude(title__iexact=title_safe)
        if title_filter.exists():
            form.add_error(
                'title', forms.ValidationError("\"%s\" is already exists ! Please try another one." % title)
                )
            return super().form_invalid(form)
        messages.add_message(self.request, messages.SUCCESS, 
        "Information Updated successfully !")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tracker:deposit_field_create')

    def get_context_data(self, **kwargs):
        context = super(CashDepositFieldUpdateView, self).get_context_data(**kwargs)
        room_instance       = self.request.user.membership.room
        deposit_fields_filter           = CashDepositField.objects.filter(room=room_instance)
        if deposit_fields_filter.exists():
            context['deposit_fields']   = deposit_fields_filter
        return context

    def user_passes_test(self, request):
        user = request.user
        if user.membership:
            object = self.get_object()
            if user.membership.role == 2 and object.room == user.membership.room:
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
        return super(CashDepositFieldUpdateView, self).dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class CashDepositFieldDeleteView(DeleteView):
    template_name   = 'tracker/deposit/delete.html'

    def get_object(self):
        slug = self.kwargs['slug']
        field_filter = CashDepositField.objects.filter(slug=slug)
        if field_filter.exists():
            return field_filter.first()
        return None

    def get_success_url(self):
        return reverse('tracker:deposit_field_create')

    def user_passes_test(self, request):
        user = request.user
        if user.membership:
            object = self.get_object()
            if user.membership.role == 2 and object.room == user.membership.room:
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
        return super(CashDepositFieldDeleteView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class CashDepositFieldAssignView(CreateView):
    template_name   = 'tracker/deposit/assign.html'
    form_class      = AssignCashDepositToMemberForm

    def get_success_url(self):
        if self.request.user.membership:
            url = reverse('tracker:deposit_chart')
        else:
            url = reverse('home')
        return url

    def get_form_kwargs(self):
        kwargs = super(CashDepositFieldAssignView, self).get_form_kwargs()
        if self.form_class:
            kwargs.update({'request': self.request})
        if kwargs['instance'] is None:
            kwargs['slug'] = self.kwargs['slug']
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CashDepositFieldAssignView, self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        room_instance = self.request.user.membership.room
        member_filter   = Membership.objects.filter(slug=slug)
        deposit_fields    = CashDepositField.objects.all()
        deposit_filter = deposit_fields.filter(room=room_instance)
        if member_filter.exists():
            member_instance = Membership.objects.get(slug=slug).user.profile.get_smallname
        else:
            member_instance = "Member"
        context["member"] = member_instance
        if deposit_filter.exists():
            context['deposit_field_exists'] = True
        return context

    def user_passes_test(self, request):
        user = request.user
        if user.membership:
            slug = self.kwargs['slug']
            membership_filter = Membership.objects.filter(slug=slug)
            if membership_filter.exists():
                member = membership_filter.first()
            if user.membership.role == 2 and user.membership.room == member.room:
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
        return super(CashDepositFieldAssignView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class CostChartView(ListView):
    template_name   = 'tracker/cost-chart.html'
    
    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        user_membership_filter = Membership.objects.filter(user=user).only('user')
        if user_membership_filter.exists():
            user_membership = Membership.objects.get(slug=user.membership.slug)
            room_instance   = user_membership.room
            member_trackers_filter = MemberTrack.objects.filter(member__room=room_instance).only('member')
            if member_trackers_filter.exists():
                query = member_trackers_filter
                return query
        return None

    def get_context_data(self, **kwargs):
        context             = super(CostChartView, self).get_context_data(**kwargs)
        user                = self.request.user
        now                 = datetime.datetime.now()
        user_membership_filter = Membership.objects.filter(user=user).only('user')
        if user_membership_filter.exists():
            user_membership = Membership.objects.get(slug=user.membership.slug)
            room_instance   = user_membership.room
            room_trackers_filter = TrackerField.objects.filter(room=room_instance).only('room')
            if room_trackers_filter.exists():
                context['fields'] = room_trackers_filter
            room_members_filter = Membership.objects.filter(room=room_instance).only('room')
            if room_members_filter.exists():
                context['members'] = room_members_filter
            total_filter = TotalHolder.objects.filter(member__room=room_instance).only('member')
            if total_filter.exists():
                context['totals'] = total_filter
                context['total_cost_room'] = total_filter.first().get_total_cost_sector_room
        return context

    def user_passes_test(self, request):
        user = request.user
        if user.membership:
            if user.membership.role == 1 or user.membership.role == 2:
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
        return super(CostChartView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class MealChartView(ListView):
    template_name   = 'tracker/meal/meal-chart-overview.html'
    
    def get_queryset(self, *args, **kwargs):
        user        = self.request.user
        now         = datetime.datetime.now()
        next_day    = (datetime.date.today() + datetime.timedelta(days=1))
        day_range   = calendar.monthrange(now.year, now.month)[1]
        user_membership_filter = Membership.objects.filter(user=user)
        if user_membership_filter.exists():
            user_membership = Membership.objects.get(slug=user.membership.slug)
            room_instance   = user_membership.room
            if now.day < day_range:
                member_meals_filter = Meal.objects.filter(
                    member__room=room_instance, meal_date__day__lte=next_day.day, meal_date__month=now.month, meal_date__year=now.year
                )
            else:
                member_meals_filter = Meal.objects.filter(
                    member__room=room_instance, meal_date__day__lte=now.day, meal_date__month=now.month, meal_date__year=now.year
                )
            if member_meals_filter.exists():
                query = member_meals_filter.order_by('member__created_at')
                return query
        return None

    def get_context_data(self, **kwargs):
        context         = super(MealChartView, self).get_context_data(**kwargs)
        user            = self.request.user
        now             = datetime.datetime.now()
        next_day        = (datetime.date.today() + datetime.timedelta(days=1))
        day_range       = calendar.monthrange(now.year, now.month)[1]
        def daterange(start_date, end_date):
            for n in range(int ((end_date - start_date).days) + 1):
                yield start_date + datetime.timedelta(n)
        start_date      = datetime.date(now.year, now.month, 1)
        if now.day < day_range:
            end_date        = datetime.date(now.year, now.month, next_day.day)
        else:
            end_date        = datetime.date(now.year, now.month, now.day)
        user_membership_filter = Membership.objects.filter(user=user).only('user')
        if user_membership_filter.exists():
            user_membership = Membership.objects.get(slug=user.membership.slug)
            room_instance   = user_membership.room
            room_members_filter = Membership.objects.filter(room=room_instance).only('user')
            if room_members_filter.exists():
                context['members'] = room_members_filter.order_by('created_at')
            context['dates'] = daterange(start_date, end_date)
            context['time'] = now
            if now.day == day_range:
                meal_next_month = Meal.objects.filter(
                    member__room=room_instance, meal_date__day=next_day.day, meal_date__month=next_day.month, meal_date__year=next_day.year
                ).only('meal_today')
                if meal_next_month.exists():
                    context['next_month_meal'] = meal_next_month
                    context['next_date'] = next_day
            total_filter = TotalHolder.objects.filter(member__room=room_instance)
            if total_filter.exists():
                context['totals'] = total_filter.order_by('member__created_at')
                context['total_meal_room'] = total_filter.first().get_total_meal_room
        return context

    def user_passes_test(self, request):
        user = request.user
        membership_filter = Membership.objects.filter(user=user)
        if membership_filter.exists():
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
        return super(MealChartView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ShoppingChartView(ListView):
    template_name   = 'tracker/shopping/chart.html'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        now  = datetime.datetime.now()
        membership_filter = Membership.objects.filter(user=user)
        if membership_filter.exists():
            membership_instance = Membership.objects.get(user=user)
            shop_type_filter = ManagerialSetting.objects.filter(room=membership_instance.room)
            if shop_type_filter.exists():
                shop_type = shop_type_filter.first().shopping_type
                if shop_type == 0:
                    shopping_filter = Shopping.objects.filter(created_by__room=membership_instance.room, shop_type=0, date__month=now.month, date__year=now.year)
                else:
                    shopping_filter = Shopping.objects.filter(created_by__room=membership_instance.room, shop_type=1, date__month=now.month, date__year=now.year)
            if shopping_filter.exists():
                query = shopping_filter.order_by('-created_at')
                return query
        return None

    def get_context_data(self, **kwargs):
        context             = super(ShoppingChartView, self).get_context_data(**kwargs)
        user                = self.request.user
        now                 = datetime.datetime.now()
        user_membership_filter = Membership.objects.filter(user=user).only('user')
        if user_membership_filter.exists():
            user_membership = Membership.objects.get(slug=user.membership.slug)
            room_instance   = user_membership.room
            room_members_filter = Membership.objects.filter(room=room_instance).only('room')
            if room_members_filter.exists():
                context['members'] = room_members_filter
            total_filter = TotalHolder.objects.filter(member__room=room_instance).only('member')
            if total_filter.exists():
                context['totals'] = total_filter
                context['room_total_shopping'] = total_filter.first()
            shop_type_filter = ManagerialSetting.objects.filter(room=room_instance)
            if shop_type_filter.exists():
                shop_type = shop_type_filter.first().shopping_type
                if shop_type == 0:
                    shopping_filter = Shopping.objects.filter(created_by__room=room_instance, shop_type=1, date__month=now.month, date__year=now.year)
                    if shopping_filter.exists():
                        context['managerial_shop'] = shopping_filter
        return context

    def user_passes_test(self, request):
        user = request.user
        if user.membership:
            if user.membership.role == 1 or user.membership.role == 2:
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
        return super(ShoppingChartView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class DepositChartView(ListView):
    template_name   = 'tracker/deposit/chart.html'

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        now  = datetime.datetime.now()
        member_deposit_filter = CashDepositMember.objects.filter(member__room=user.membership.room, created_at__month=now.month, created_at__year=now.year)
        if member_deposit_filter.exists():
            return member_deposit_filter
        return None

    def get_context_data(self, **kwargs):
        context             = super(DepositChartView, self).get_context_data(**kwargs)
        user                = self.request.user
        # now                 = datetime.datetime.now()
        room_members_filter = Membership.objects.filter(room=user.membership.room)
        if room_members_filter.exists():
            context['members'] = room_members_filter
            deposit_field_filter = CashDepositField.objects.filter(room=user.membership.room)
            if deposit_field_filter.exists():
                context['fields'] = deposit_field_filter
        total_filter = TotalHolder.objects.filter(member__room=user.membership.room).only('member')
        if total_filter.exists():
            context['totals'] = total_filter
            context['total_room_deposit'] = total_filter.first().get_deposit_total_room
        return context

    def user_passes_test(self, request):
        user = request.user
        if user.membership:
            if user.membership.role == 1 or user.membership.role == 2:
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
        return super(DepositChartView, self).dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class AnalyticsView(ListView):
    template_name   = 'tracker/analytics/analytics.html'
    queryset        = MemberTrack.objects.all()

    def get_queryset(self, *args, **kwargs):
        request = self.request
        room_instance   = request.user.membership.room
        query   = MemberTrack.objects.filter(member__room=room_instance)
        return query