from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.views.generic import DetailView, UpdateView, ListView
from .models import UserProfile
from suspicious.models import Suspicious
from .forms import UserProfileUpdateForm
from django import forms
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import datetime

@method_decorator(login_required, name='dispatch')
class UserProfileView(DetailView):
    queryset        = UserProfile.objects.all()
    template_name   = 'profile/index.html'

    def get_object(self):
        return UserProfile.objects.get(slug=self.kwargs['slug'])

@method_decorator(login_required, name='dispatch')
class UserProfileUpdateView(UpdateView):
    template_name   = 'profile/update.html'
    form_class      = UserProfileUpdateForm

    def get_object(self):
        return UserProfile.objects.get(slug=self.kwargs['slug'])
        
    def user_passes_test(self, request):
        if request.user.is_authenticated:
            self.object = self.get_object()
            return self.object.user == request.user
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
        return super(UserProfileUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        slug = self.kwargs['slug']
        messages.add_message(self.request, messages.SUCCESS, 
        "Your profile has been updated successfully !")
        return reverse('profile', kwargs={'slug': slug})

class UserPublicProfileView(DetailView):
    queryset        = UserProfile.objects.all()
    template_name   = 'profile/public.html'

    def get_object(self, *args, **kwargs):
        request = self.request
        slug    = self.kwargs.get('slug')
        try:
            instance = UserProfile.objects.get(slug=slug)
        except UserProfile.DoesNotExist:
            raise Http404("Not Found !!!")
        except UserProfile.MultipleObjectsReturned:
            qs = UserProfile.objects.filter(slug=slug)
            instance = qs.first()
        except:
            raise Http404("Something went wrong !!!")

        return instance
    
    def get_context_data(self, **kwargs):
        context             = super(UserPublicProfileView, self).get_context_data(**kwargs)
        user_instance       = self.request.user
        if user_instance.is_authenticated:
            profile_instance    = self.object.user
            if user_instance == profile_instance:
                context['modifier'] = True
        return context

class UserListView(ListView):
    model               = UserProfile
    context_object_name = 'objects'
    template_name       ='profile/list.html'
    paginate_by         = 12

    def get_queryset(self, *args, **kwargs):
        request = self.request
        query   = UserProfile.objects.all().latest()
        return query

    def get_context_data(self, **kwargs):
        context         = super(UserListView, self).get_context_data(**kwargs)
        users           = UserProfile.objects.all()
        user_counter    = users.count()
        context["total_users"] = user_counter
        return context
    