
Must Implement Only Email Varified User can Login to the sight.
# Implement Contact Number start with +880 auto
# After room create auto redirect to room
=================== Choices Map =================
# User Gender Choices
    MALE        = 'M'
    FEMALE      = 'F'
    OTHERS      = 'O'
# User Type Choices
    REGULAR     = 0
    PREMIUM     = 1
# Room Privacy Choices
    PUBLIC      = 0
    MEMBERS     = 1
    SECRET      = 2
# Membership Role Choices
    MEMBER      = 0
    SUPERVISOR  = 1
    MANAGER     = 2

# Shopping Type Choices
    INDIVIDUAL_MEMBER_DEPENDENT_SHOPPING    = 0
    ROOM_MANAGER_DEPENDENT_SHOPPING         = 1


# notify_type
    - meal_update               - identifier(meal-slug)
    - meal_update_by_maintainer - identifier(meal-slug)
    - meal_update_confirmed     - identifier(message)
    - meal_request_cancel       - identifier(message)
    - join_room                 - identifier(room-slug)

=================== Model Architecture =================

# User
    - username          (CharField)
    - first_name        (CharField)
    - last_name         (CharField)
    - email             (EmailField)
    - password          (CharField)
    - groups            (ManyToManyField)       to - Group
    - user_permissions  (ManyToManyField)       to - Permission
    - is_staff          (BooleanField)
    - is_active         (BooleanField)
    - is_superuser      (BooleanField)
    - last_login        (DateTimeField)
    - date_joined       (DateTimeField)

# UserProfile
    - user          (OneToOneField)             to - User (profile)
    - slug          (SlugField)
    - role          (PositiveSmallIntegerField)
    - contact       (CharField)
    - gender        (CharField)
    - image         (CharField)
    - about         (TextField)
    - address       (CharField)
    - facebook      (CharField)
    - linkedin      (CharField)
    - website       (CharField)
    - updated_at    (DateTimeField)

# Room
    - title         (CharField)
    - slug          (SlugField)
    - is_active     (BooleanField)
    - privacy       (PositiveSmallIntegerField)
    - description   (TextField)
    - creator       (OneToOneField)             to  - User (creator)
    - created_at    (DateTimeField)
    - updated_at    (DateTimeField)

# ManagerialSetting
    - room          (ForeignKey)                to  - Room (managerial_setting)
    - shopping_type (PositiveSmallIntegerField)
    - is_CUD_able   (BooleanField)
    - created_at    (DateTimeField)
    - updated_at    (DateTimeField)

# Membership
    - user          (OneToOneField)             to  - User (membership)
    - role          (PositiveSmallIntegerField)
    - room          (ForeignKey)                to  - Room (room)
    - slug          (SlugField)
    - created_at    (DateTimeField)
    - updated_at    (DateTimeField)

# MemberRequest
    - user          (OneToOneField)             to  - User (member_request)
    - room          (ForeignKey)                to  - Room (member_request_room)
    - slug          (SlugField)
    - created_at    (DateTimeField)
    - updated_at    (DateTimeField)

# Meal
    - member            (ForeignKey)                to  - Membership (member_meal)
    - slug              (SlugField)
    - meal_today        (DecimalField)
    - meal_next_day     (DecimalField)
    - auto_entry        (BooleanField)
    - auto_entry_value  (DecimalField)
    - meal_date         (DateTimeField)
    - confirmed_by      (ForeignKey)                to  - Membership (confirmed_by)
    - created_at        (DateTimeField)
    - updated_at        (DateTimeField)

# MealUpdateRequest
    - member            (ForeignKey)                to  - Membership (member_meal_update)
    - slug              (SlugField)
    - meal_shoul_be     (DecimalField)
    - request_to        (ForeignKey)                to  - Membership (request_to)
    - created_at        (DateTimeField)
    - updated_at        (DateTimeField)

# TrackerField
    - title         (CharField)
    - room          (ForeignKey)                to  - Room (tracker_field_room)
    - slug          (SlugField)
    - description   (TextField)
    - created_at    (DateTimeField)
    - updated_at    (DateTimeField)

# MemberTrack
    - member        (ForeignKey)                to  - Membership (member_track)
    - tracker_field (ForeignKey)                to  - TrackerField (member_track_field)
    - cost          (DecimalField)
    - created_at    (DateTimeField)
    - updated_at    (DateTimeField)

# Shopping
    - created_by    (ForeignKey)                to  - Membership (member_shopping)
    - item          (CharField)
    - slug          (SlugField)
    - quantity      (DecimalField)
    - quantity_unit (CharField)
    - cost          (DecimalField)
    - date          (DateField)
    - shop_type     (PositiveSmallIntegerField)
    - created_at    (DateTimeField)
    - updated_at    (DateTimeField)

# CashDepositField
    - title         (CharField)
    - description   (TextField)
    - slug          (SlugField)
    - room          (ForeignKey)                to  - Room (deposit_field_room)
    - created_at    (DateTimeField)
    - updated_at    (DateTimeField)

# CashDepositMember
    - deposit_field (ForeignKey)                to  - CashDepositField (member_deposit_field)
    - amount        (DecimalField)
    - member        (ForeignKey)                to  - Membership (member_cash_deposit)
    - created_at    (DateTimeField)
    - updated_at    (DateTimeField)

# TotalHolder
    - member            (ForeignKey)                to  - Membership (member_total_holder)
    - created_at        (DateTimeField)
    - updated_at        (DateTimeField)

# Suspicious
    - user          (ForeignKey)                to  - User (suspicious)
    - attempt       (PositiveSmallIntegerField)
    - first_attempt (DateTimeField)
    - last_attempt  (DateTimeField)

# Notification
    - sender            (ForeignKey)                to  - UserProfile (notification_sender)
    - receiver          (ForeignKey)                to  - UserProfile (notification_receiver)
    - slug              (SlugField)
    - category          (CharField)
    - notify_type       (CharField)
    - identifier        (CharField)
    - room_identifier   (CharField)
    - counter           (PositiveSmallIntegerField)
    - message           (CharField)
    - created_at        (DateTimeField)
    - updated_at        (DateTimeField)



# ===================== Important Codes Snippets ================= #
# ----------------- Validate User for update view ----------------
    from django.http import HttpResponseRedirect
    from suspicious.models import Suspicious
    from django.contrib import messages
    import datetime

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

# --------------------- Get Form kwargs ----------------------
    def get_form_kwargs(self):
        kwargs = super(MealCreateView, self).get_form_kwargs()
        if self.form_class:
            kwargs.update({'request': self.request})
        return kwargs

# ----------- Notification Creation Starts -----------
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
                counter = counter
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
                message="%s rejected your request to update meal of %s" %(meal_request_notify_instance.request_to, meal_instance.meal_date.strftime("%B-%d-%Y"))
            )
# ----------- Notification Creation Ends -----------
notify_slug = notify_receiver_instance.username.lower()+'-'+time_str_mix_slug()
Notification.objects.create(
    sender=notify_sender_instance,
    receiver=notify_receiver_instance,
    slug=notify_slug,
    notify_type=notify_type,
    room_identifier=room_slug,
    counter=1,
    message="%s rejected your request to update meal of %s" %(meal_request_notify_instance.request_to, meal_instance.meal_date.strftime("%B-%d-%Y"))
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


# ----------- Calculation Deletion Starts -----------
def post(self, request, *args, **kwargs):
        response = super(MealUpdateRequestConfirmView, self).post(request, *args, **kwargs)
        user = self.request.user
        now  = datetime.datetime.now()
        members_filter = Membership.objects.filter(room=user.membership.room)
        if members_filter.exists():
            for member in members_filter:
                meal_filter = Meal.objects.filter(
                    member=member, meal_date__day__lte=now.day, meal_date__month=now.month, meal_date__year=now.year, member__room=member.room
                )
                if meal_filter.exists():
                    total_calculate = meal_filter.aggregate(total=Sum(F('meal_today')))
                    total = total_calculate['total']
                    existed_total = TotalHolder.objects.filter(member=member)
                    if existed_total.exists():
                        existed_total.update(
                            meal_total = total
                        )
                    else:
                        TotalHolder.objects.create(
                            member = member,
                            meal_total = total
                        )
        return response

# ----------- Calculation Deletion Ends -----------

# ----------- Back URL -----------
url = request.META.get('HTTP_REFERER', '/')