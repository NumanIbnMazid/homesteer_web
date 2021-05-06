from django import template
import datetime
from django.db.models import Q
from accounts.models import UserProfile
from rooms.models import ManagerialSetting
from memberships.models import Membership, MemberRequest
from tracker.models import Meal, TrackerField
from utils.models import Notification

register = template.Library()

@register.simple_tag(takes_context=True)
def is_pending_member_tag(context):
    request     = context['request']
    if MemberRequest.objects.filter(user=request.user).exists():
        return True
    return False


@register.simple_tag(takes_context=True)
def is_member_tag(context):
    request     = context['request']
    if Membership.objects.filter(user=request.user).exists():
        return True
    return False

@register.simple_tag(takes_context=True)
def member_tag(context):
    request     = context['request']
    if Membership.objects.filter(user=request.user).exists():
        return Membership.objects.filter(user=request.user).first()
    return False

@register.simple_tag(takes_context=True)
def is_creator_tag(context):
    request     = context['request']
    member      = request.user.membership
    if member.room.creator == request.user:
        is_creator = True
        return is_creator
    return False

@register.simple_tag(takes_context=True)
def is_manager_tag(context):
    request     = context['request']
    member      = request.user.membership
    if member.role == 2:
        return True
    return False

@register.simple_tag(takes_context=True)
def is_supervisor_tag(context):
    request     = context['request']
    member      = request.user.membership
    if member.role == 1:
        return True
    return False

@register.simple_tag(takes_context=True)
def is_modifier_tag(context):
    request     = context['request']
    member      = request.user.membership
    if member.room.creator == request.user or member.role == 2:
        return True
    return False

@register.simple_tag(takes_context=True)
def is_maintainer_tag(context):
    request     = context['request']
    member      = request.user.membership
    if member.room.creator == request.user or member.role == 2 or member.role == 1:
        return True
    return False

@register.simple_tag(takes_context=True)
def meal_slug_tag(context):
    request         = context['request']
    now             = datetime.datetime.now()
    member          = request.user.membership
    existed_meal_filter = Meal.objects.filter(
                    Q(meal_date__day=now.day, meal_date__month=now.month, meal_date__year=now.year),
                    member=member
                    )
    if existed_meal_filter.exists():
        existed_meal_check = Meal.objects.filter(
                    Q(meal_date__day=now.day, meal_date__month=now.month, meal_date__year=now.year),
                    member=member
                    ).last()
        return existed_meal_check.slug
    return None
        
@register.simple_tag(takes_context=True)
def notification_tag(context):
    request     = context['request']
    user        = request.user
    if UserProfile.objects.filter(user=user).exists():
        user_instance = UserProfile.objects.get(user=user)
        notification_receiver_filter = Notification.objects.filter(receiver=user_instance).order_by('-updated_at')
        if notification_receiver_filter.exists():
            return notification_receiver_filter
    return None

@register.simple_tag(takes_context=True)
def room_setting_tag(context):
    request     = context['request']
    member      = request.user.membership
    room_setting_filter = ManagerialSetting.objects.filter(room=member.room)
    if room_setting_filter.exists():
        return room_setting_filter.first()
    return False