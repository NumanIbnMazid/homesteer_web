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
import re
from django.contrib import messages
from django.core.validators import MinValueValidator
from decimal import Decimal
import datetime
import time
from django.urls import reverse
from django.db.models import Q
from accounts.utils import time_str_mix_slug
from django.db.models import F, Sum


class DateInput(forms.DateInput):
    input_type = 'date'

class TrackerFieldCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TrackerFieldCreateForm, self).__init__(*args, **kwargs)
        self.fields['title']        = forms.CharField(max_length=20, 
            widget=forms.TextInput()
        )
        self.fields['description']  = forms.CharField(required=False, max_length=30, label="Help Text",
            widget=forms.Textarea(attrs={'rows': 1, 'cols': 2})
        )
        self.fields['title'].help_text = "Cost fields are like Room-Rent, Internet-Bill, Service-Charge etc."
        self.fields['description'].help_text = "Keep some tiny information about the field if you need. It's not mandatory."

    class Meta:
        model   = TrackerField
        fields  = ['title', 'room', 'description']
        exclude = ['room']

    def clean_title(self):
        title   = self.cleaned_data.get('title')
        room    = self.request.user.membership.room
        title_filter        = TrackerField.objects.filter(title__iexact=title, room=room)
        if title_filter.exists():
            title_instance  = TrackerField.objects.get(title__iexact=title, room=room)
            raise forms.ValidationError(
                "\"%s\" Field is already exists ! Please try another one." % title_instance
            )
        if not title == None :
            allowed_chars   = re.match(r'^[0-9A-Za-z-]+$', title)
            length          = len(title)

            if not allowed_chars:
                raise forms.ValidationError('Please remove any special characters or spaces. Only Alpha Numeric values and "-" are allowed!')
            if length > 20:
                raise forms.ValidationError('Maximum 20 characters allowed !')
        return title

    def save(self):
        title       = self.cleaned_data.get('title')
        description = self.cleaned_data.get('description')
        user        = self.request.user
        room        = user.membership.room
        slug_binding    = title.lower()+'-'+time_str_mix_slug()
        TrackerField.objects.create(
            title = title,
            description = description,
            room = room,
            slug = slug_binding
        )
        messages.add_message(self.request, messages.SUCCESS,
        "Cost sector \"%s\" created successfully !" %title)
        tracker_filter = TrackerField.objects.filter(room=room, slug=slug_binding)
        if tracker_filter.exists():
            now             = datetime.datetime.now()
            tracker_instance = TrackerField.objects.get(room=room, slug=slug_binding)
            member_filter   = Membership.objects.filter(room=room)
            if member_filter.exists():
                for member in member_filter:
                    MemberTrack.objects.create(
                        member=member,
                        tracker_field=tracker_instance,
                        cost=0
                    )


class TrackerFieldUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TrackerFieldUpdateForm, self).__init__(*args, **kwargs)
        self.fields['title']        = forms.CharField(max_length=20, 
            widget=forms.TextInput()
        )
        self.fields['description']  = forms.CharField(required=False, max_length=30, label="Help Text",
            widget=forms.Textarea(attrs={'rows': 1, 'cols': 2})
        )
        self.fields['title'].help_text = "Cost fields are like Room-Rent, Internet-Bill, Service-Charge etc."
        self.fields['description'].help_text = "Keep some tiny information about the field if you need. It's not mandatory."
    
    class Meta:
        model   = TrackerField
        fields  = ['title', 'room', 'description']
        exclude = ['room']

    def clean_title(self):
        title   = self.cleaned_data.get('title')
        if not title == None :
            allowed_chars   = re.match(r'^[0-9A-Za-z-]+$', title)
            length          = len(title)

            if not allowed_chars:
                raise forms.ValidationError('Please remove any special characters or spaces. Only Alpha Numeric values and "-" are allowed!')
            if length > 20:
                raise forms.ValidationError('Maximum 20 characters allowed !')
        return title

class AssignFieldToMemberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.slug = kwargs.pop('slug', None)
        super(AssignFieldToMemberForm, self).__init__(*args, **kwargs)
        user = self.request.user
        room_instance   = user.membership.room
        membership_cross_check = Membership.objects.filter(
            slug=self.slug,
            room=user.membership.room
        )
        if membership_cross_check.exists():
            maintainer_filter = Membership.objects.filter(
                Q(role=1) | Q(role=2),
                user=user,
                room=room_instance
            )
            if maintainer_filter.exists():
                tracker_fields  = TrackerField.objects.filter(room=room_instance)
                tracked_members = MemberTrack.objects.all()
                for i in range(len(tracker_fields)):
                    title = tracker_fields[i].title
                    field_name = '%s' % (title, )
                    self.fields[field_name] = forms.DecimalField(
                        required=False, decimal_places=2, max_digits=7, validators=[MinValueValidator(Decimal('0.00'))]
                        )
                    try:
                        self.fields[field_name].help_text = tracker_fields[i].description
                        cost_filter = tracked_members.filter(member__slug=self.slug, tracker_field__title=field_name)
                        if cost_filter.exists():
                            for cost_instance in cost_filter:
                                cost_instant = cost_instance.cost
                            self.initial[field_name] = cost_instant
                        else:
                            self.initial[field_name] = 0.00
                    except IndexError:
                        self.initial[field_name] = ""

    class Meta:
        model   = MemberTrack
        exclude = ['member', 'tracker_field', 'cost']

    def save(self):
        member_instance     = self.slug
        room_instance       = self.request.user.membership.room
        membership_cross_check = Membership.objects.filter(
            slug=self.slug,
            room=room_instance
        )
        if membership_cross_check.exists():
            maintainer_filter = Membership.objects.filter(
                Q(role=1) | Q(role=2),
                user=self.request.user,
                room=room_instance
            )
            member_objects = Membership.objects.filter(slug=member_instance)
            if member_objects.exists():
                member = Membership.objects.get(slug=member_instance)
                if maintainer_filter.exists():
                    now                 = datetime.datetime.now()
                    for fields in self.cleaned_data:
                        tracker_fields = TrackerField.objects.filter(title=fields)
                        if tracker_fields.exists():
                            tracker_field = TrackerField.objects.get(title=fields, room=room_instance)
                            value = self.cleaned_data.get(fields)
                            member_track_filter = MemberTrack.objects.filter(
                                member=member, tracker_field = tracker_field
                            )
                            if member_track_filter.exists():
                                member_track_filter.update(
                                    cost = value
                                )
                            else:
                                MemberTrack.objects.get_or_create(
                                    member = member,
                                    tracker_field = tracker_field,
                                    cost = value
                                )
                    messages.add_message(self.request, messages.SUCCESS,
                    "Cost Fields allocated successfully !")
                else:
                    messages.add_message(self.request, messages.WARNING,
                    "Something went wrong !")
        else:
            instance_user   = self.request.user
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

class MealEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MealEntryForm, self).__init__(*args, **kwargs)
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%B-%d-%Y")
        self.fields['meal_today'].help_text = "Enter your meal of today (%s)" % time.strftime("%B-%d-%Y")
        self.fields['meal_next_day'].help_text = "Enter your meal of tomorrow (%s)" % tomorrow
        self.fields['auto_entry_value'].help_text = "The number of meal you want to automatically added everyday. You can update meal on daily basis. Keep it blank if you want to manage your meal entry manually"

    class Meta:
        model   = Meal
        fields  = ['meal_today', 'meal_next_day', 'auto_entry_value']
        exclude = ['auto_entry']

class MealUpdateForm(forms.ModelForm):
    meal_now = forms.CharField(required=False)
    def __init__(self, *args, **kwargs):
        self.request    = kwargs.pop('request', None)
        super(MealUpdateForm, self).__init__(*args, **kwargs)
        next_day        = (datetime.date.today() + datetime.timedelta(days=1))
        tomorrow        = next_day.strftime("%B-%d-%Y")
        tomorrow_day    = next_day.strftime("%d")
        tomorrow_month  = next_day.strftime("%m")
        tomorrow_year   = next_day.strftime("%Y")
        self.fields['meal_now'].label = "Meal Today"
        self.fields['meal_now'].help_text = "Meal of today (%s)" % time.strftime("%B-%d-%Y")
        self.fields['meal_now'].widget.attrs['readonly'] = True
        self.fields['meal_next_day'].help_text = "Enter your meal of tomorrow (%s)" % tomorrow
        self.fields['auto_entry_value'].help_text = "The number of meal you want to automatically added everyday. You can update meal on daily basis. Keep it blank if you want to manage your meal entry manually"
        existed_meal_filter = Meal.objects.filter(member__user=self.request.user)
        now                 = datetime.datetime.now()
        if existed_meal_filter.exists():
            existed_meal_instance = existed_meal_filter.filter(
                        Q(meal_date__day=now.day, meal_date__month=now.month, meal_date__year=now.year)
                        ).last()
            meal_tomorrow_filter = existed_meal_filter.filter(
                        Q(meal_date__day=tomorrow_day, meal_date__month=tomorrow_month, meal_date__year=tomorrow_year)
                    )
            if meal_tomorrow_filter.exists():
                meal_tomorrow_instance = existed_meal_filter.filter(
                        Q(meal_date__day=tomorrow_day, meal_date__month=tomorrow_month, meal_date__year=tomorrow_year)
                    ).last()
            if existed_meal_instance:
                if existed_meal_instance.meal_date.strftime("%m-%d-%Y") == now.strftime("%m-%d-%Y"):
                    self.initial['meal_now']          = existed_meal_instance.meal_today
                    if meal_tomorrow_filter.exists():
                        self.initial['meal_next_day']   = meal_tomorrow_instance.meal_today
                    else:
                        self.initial['meal_next_day']   = 0.00
                    self.initial['auto_entry_value']        = existed_meal_instance.auto_entry_value
            else:
                self.initial['meal_now']          = 0.00
                self.initial['meal_next_day']       = 0.00
                self.initial['auto_entry_value']    = 0.00
    class Meta:
        model   = Meal
        fields  = ['meal_now', 'meal_next_day', 'auto_entry_value']
        exclude = ['auto_entry']

class MealUpdateAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MealUpdateAdminForm, self).__init__(*args, **kwargs)
        self.fields['meal_today'].help_text = "Enter meal of today (%s)" % time.strftime("%B-%d-%Y")

    class Meta:
        model   = Meal
        fields  = ['meal_today']
        exclude = ['auto_entry', 'meal_next_day', 'auto_entry_value']

class MealUpdateRequestForm(forms.ModelForm):
    meal_previous = forms.CharField(required=False)
    def __init__(self, *args, **kwargs):
        self.request    = kwargs.pop('request', None)
        self.slug = kwargs.pop('slug', None)
        super(MealUpdateRequestForm, self).__init__(*args, **kwargs)
        slug = self.slug
        user = self.request.user
        if Membership.objects.filter(user=user).exists():
            if Meal.objects.filter(slug=slug).exists():
                if len(Membership.objects.filter(room=user.membership.room)) < 2:
                    REQUEST_TO_QUERYSET = Membership.objects.filter(
                            room = user.membership.room
                        )
                else:
                    if user.membership.role == 0:
                        REQUEST_TO_QUERYSET = Membership.objects.filter(
                            Q(role=1) | Q(role=2),
                            room = user.membership.room
                        ).exclude(user=user)
                    else:
                        initial_receiver = Membership.objects.filter(
                            Q(role=1) | Q(role=2),
                            room = user.membership.room
                        ).exclude(user=user)
                        if initial_receiver.exists():
                            REQUEST_TO_QUERYSET = initial_receiver
                        else:
                            REQUEST_TO_QUERYSET = Membership.objects.filter(
                            room = user.membership.room
                        ).exclude(user=user)
                meal_instance = Meal.objects.get(slug=slug)
                self.initial['meal_previous']  = meal_instance.meal_today
                self.fields['meal_previous'].help_text = "Meal of %s" %meal_instance.meal_date.strftime("%B-%d-%Y")
                self.fields['meal_previous'].widget.attrs['readonly'] = True
                self.fields['meal_should_be'].help_text = "Your desired number of meal for the day"
                self.fields['request_to'] = forms.ModelChoiceField(queryset=REQUEST_TO_QUERYSET, empty_label="------- SELECT -------")
                self.fields['request_to'].help_text = "Select User whom you want to send the request"
    class Meta:
        model           = MealUpdateRequest
        fields          = ['meal_previous', 'meal_should_be' , 'request_to']


class MealUpdateRequestConfirmForm(forms.ModelForm):
    meal_request = forms.CharField(required=False)
    def __init__(self, *args, **kwargs):
        self.request    = kwargs.pop('request', None)
        self.slug = kwargs.pop('slug', None)
        super(MealUpdateRequestConfirmForm, self).__init__(*args, **kwargs)
        if Meal.objects.filter(slug=self.slug).exists():
            meal_instance = Meal.objects.filter(slug=self.slug).last()
            if MealUpdateRequest.objects.filter(slug=self.slug).exists():
                meal_request_instance = MealUpdateRequest.objects.filter(slug=self.slug).last()
                self.fields['meal_request'].widget.attrs['readonly'] = True
                self.fields['meal_request'].help_text = "Claiming number of meal for %s" % meal_instance.meal_date.strftime("%B-%d-%Y")
                self.initial['meal_request']  = meal_request_instance.meal_should_be
                self.fields['meal_request'].label = "Claiming Number of Meal"
    class Meta:
        model   = Meal
        fields  = ['meal_request']
        exclude = ['meal_today', 'meal_next_day', 'auto_entry', 'auto_entry_value']


class ShoppingCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ShoppingCreateForm, self).__init__(*args, **kwargs)
        self.fields['item']        = forms.CharField(max_length=15, 
            widget=forms.TextInput()
        )
        self.fields['item'].label               = "Item Title"
        self.fields['cost'].label               = "Cost"
        self.fields['quantity'].label           = "Quantity"
        self.fields['quantity_unit'].label      = "Quantity Unit"
        self.fields['item'].help_text = "Items titles are like Rice, Fish, Handwash etc. If you don't want to entry individual item then enter item name as Monthly-Shopping, Bazar etc."
        self.fields['quantity'].help_text = "The number or measurement of item like 1, 1.5 etc."
        self.fields['quantity_unit'].help_text = "Unit of entered quantity like kg, litre, gram etc."
        self.fields['cost'].help_text = "Enter the shopping cost"
        self.fields['date'].help_text = "Enter the date of shopping"

    class Meta:
        model   = Shopping
        fields  = ['item', 'cost', 'date', 'quantity', 'quantity_unit']
        exclude = ['slug']
        widgets = {
            'date': DateInput(),
        }
        # exclude = ['room']

    def clean_item(self):
        user = self.request.user
        membership = Membership.objects.get(user=user)
        item   = self.cleaned_data.get('item')
        room    = self.request.user.membership.room
        shopping_type_filter = ManagerialSetting.objects.filter(room=room)
        if shopping_type_filter.exists():
            shopping_type = ManagerialSetting.objects.filter(room=room).first().shopping_type
            if shopping_type == 0:
                item_filter        = Shopping.objects.filter(item__iexact=item, created_by__room=room, created_by=membership, shop_type=0)
                if item_filter.exists():
                    item_instance  = Shopping.objects.filter(item__iexact=item, created_by__room=room, created_by=membership, shop_type=0).first()
                    raise forms.ValidationError(
                        "\"%s\" is already in your shopping list! Please insert another one." % item_instance.item
                    )
            else:
                item_filter        = Shopping.objects.filter(item__iexact=item, created_by__room=room, shop_type=1)
                if item_filter.exists():
                    item_instance  = Shopping.objects.filter(item__iexact=item, created_by__room=room, shop_type=1).first()
                    raise forms.ValidationError(
                        "\"%s\" is already in your shopping list! Please insert another one." % item_instance.item
                    )
        if not item == None :
            allowed_chars   = re.match(r'^[0-9A-Za-z-_]+$', item)
            length          = len(item)

            if not allowed_chars:
                raise forms.ValidationError('Please remove any special characters or spaces. Only Alpha Numeric values and "-", "_" are allowed!')
            if length > 15:
                raise forms.ValidationError('Maximum 20 characters allowed !')
        return item

    def clean(self):
        data            = self.cleaned_data
        quantity        = data.get('quantity')
        quantity_unit   = data.get('quantity_unit')
        if quantity == None and not quantity_unit == None:
            msg = "Please insert 'Quantity' first and then 'Quantity Unit' !"
            self.add_error('quantity', msg)
        return data

    def clean_quantity_unit(self):
        quantity_unit   = self.cleaned_data.get('quantity_unit')
        if not quantity_unit == None:
            allowed_chars   = re.match(r'^[A-Za-z]+$', quantity_unit)
            length          = len(quantity_unit)
            if length > 10:
                raise forms.ValidationError('Maximum 10 characters allowed !')
            if not allowed_chars:
                raise forms.ValidationError('Please remove any special characters or spaces. Only Alpha values are allowed!')
        return quantity_unit

    def clean_date(self):
        date = self.cleaned_data.get('date')
        now  = datetime.datetime.now()
        # today = datetime.date.today()
        # previous_month_date = (today.replace(day=1) - datetime.timedelta(1)).replace(day=1)
        if date.month < now.month or date.year < now.year or date.month > now.month or date.year > now.year:
            raise forms.ValidationError('Shopping date must be within this month and year!')
        return date


class ShoppingUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ShoppingUpdateForm, self).__init__(*args, **kwargs)
        self.fields['item']        = forms.CharField(max_length=15, 
            widget=forms.TextInput()
        )
        # self.initial['quantity_unit']           = "Kg"
        self.fields['item'].label               = "Item Title"
        self.fields['cost'].label               = "Cost"
        self.fields['quantity'].label           = "Quantity"
        self.fields['quantity_unit'].label      = "Quantity Unit"
        self.fields['item'].help_text = "Items titles are like Rice, Fish, Handwash etc. If you don't want to entry individual item then enter item name as Monthly-Shopping, Bazar etc."
        self.fields['quantity'].help_text = "The number or measurement of item like 1, 1.5 etc."
        self.fields['quantity_unit'].help_text = "Unit of entered quantity like kg, litre, gram etc."
        self.fields['cost'].help_text = "Enter the shopping cost"
        self.fields['date'].help_text = "Enter the date of shopping"

    class Meta:
        model   = Shopping
        fields  = ['item', 'cost', 'date', 'quantity', 'quantity_unit']
        exclude = ['slug']
        widgets = {
            'date': DateInput(),
        }

    def clean_item(self):
        item_instance   = self.instance.item
        item            = self.cleaned_data.get('item')
        if not item == item_instance:
            user = self.request.user
            membership = Membership.objects.filter(user=user).first()
            room    = self.request.user.membership.room
            shopping_type_filter = ManagerialSetting.objects.filter(room=room)
            if shopping_type_filter.exists():
                shopping_type = ManagerialSetting.objects.filter(room=room).first().shopping_type
                if shopping_type == 0:
                    item_filter        = Shopping.objects.filter(item__iexact=item, created_by__room=room, created_by=membership, shop_type=0)
                    if item_filter.exists():
                        item_instance  = Shopping.objects.filter(item__iexact=item, created_by__room=room, created_by=membership, shop_type=0).first()
                        raise forms.ValidationError(
                            "\"%s\" is already in your shopping list! Please insert another one." % item_instance.item
                        )
                else:
                    item_filter        = Shopping.objects.filter(item__iexact=item, created_by__room=room, shop_type=1)
                    if item_filter.exists():
                        item_instance  = Shopping.objects.filter(item__iexact=item, created_by__room=room, shop_type=1).first()
                        raise forms.ValidationError(
                            "\"%s\" is already in your shopping list! Please insert another one." % item_instance.item
                        )
            if not item == None :
                allowed_chars   = re.match(r'^[0-9A-Za-z-_]+$', item)
                length          = len(item)

                if not allowed_chars:
                    raise forms.ValidationError('Please remove any special characters or spaces. Only Alpha Numeric values and "-", "_" are allowed!')
                if length > 15:
                    raise forms.ValidationError('Maximum 20 characters allowed !')
        return item

    def clean(self):
        data            = self.cleaned_data
        quantity        = data.get('quantity')
        quantity_unit   = data.get('quantity_unit')
        if quantity == None and not quantity_unit == None:
            msg = "Please insert 'Quantity' first and then 'Quantity Unit' !"
            self.add_error('quantity', msg)
        return data

    def clean_quantity_unit(self):
        quantity_unit   = self.cleaned_data.get('quantity_unit')
        if not quantity_unit == None:
            allowed_chars   = re.match(r'^[A-Za-z]+$', quantity_unit)
            length          = len(quantity_unit)
            if length > 10:
                raise forms.ValidationError('Maximum 10 characters allowed !')
            if not allowed_chars:
                raise forms.ValidationError('Please remove any special characters or spaces. Only Alpha values are allowed!')
        return quantity_unit

    def clean_date(self):
        date = self.cleaned_data.get('date')
        now  = datetime.datetime.now()
        # today = datetime.date.today()
        # previous_month_date = (today.replace(day=1) - datetime.timedelta(1)).replace(day=1)
        if date.month < now.month or date.year < now.year or date.month > now.month or date.year > now.year:
            raise forms.ValidationError('Shopping date must be within this month and year!')
        return date


class CashDepositFieldCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CashDepositFieldCreateForm, self).__init__(*args, **kwargs)
        self.fields['title']        = forms.CharField(max_length=20, 
            widget=forms.TextInput()
        )
        self.fields['title'].help_text  = "Ex: Shopping-Deposit, Monthly-Deposit etc."
        self.fields['description']  = forms.CharField(required=False, max_length=30, label="Help Text",
            widget=forms.Textarea(attrs={'rows': 1, 'cols': 2})
        )
        self.fields['description'].help_text = "Keep some tiny information about the field if you need. It's not mandatory."

    class Meta:
        model   = CashDepositField
        fields  = ['title', 'description']
        exclude = ['slug']

    def clean_title(self):
        title   = self.cleaned_data.get('title')
        if not title == None :
            allowed_chars   = re.match(r'^[0-9A-Za-z-]+$', title)
            length          = len(title)

            if not allowed_chars:
                raise forms.ValidationError('Please remove any special characters or spaces. Only Alpha Numeric values and "-" are allowed!')
            if length > 20:
                raise forms.ValidationError('Maximum 20 characters allowed !')
        return title

    def clean_description(self):
        description   = self.cleaned_data.get('description')
        if not description == None :
            length          = len(description)
            if length > 30:
                raise forms.ValidationError('Maximum 30 characters allowed !')
        return description

class AssignCashDepositToMemberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.slug = kwargs.pop('slug', None)
        super(AssignCashDepositToMemberForm, self).__init__(*args, **kwargs)
        user = self.request.user
        room_instance   = user.membership.room
        membership_cross_check = Membership.objects.filter(
            slug=self.slug,
            room=user.membership.room
        )
        if membership_cross_check.exists():
            maintainer_filter = Membership.objects.filter(
                Q(role=2),
                user=user,
                room=room_instance
            )
            if maintainer_filter.exists():
                deposit_field  = CashDepositField.objects.filter(room=room_instance)
                deposited_members = CashDepositMember.objects.all()
                for i in range(len(deposit_field)):
                    title = deposit_field[i].title
                    field_name = '%s' % (title, )
                    self.fields[field_name] = forms.DecimalField(
                        required=False, decimal_places=2, max_digits=7, validators=[MinValueValidator(Decimal('0.00'))]
                        )
                    try:
                        self.fields[field_name].help_text = deposit_field[i].description
                        deposit_filter = deposited_members.filter(member__slug=self.slug, deposit_field__title=field_name)
                        if deposit_filter.exists():
                            for deposit in deposit_filter:
                                amount = deposit.amount
                            self.initial[field_name] = amount
                        else:
                            self.initial[field_name] = 0.00
                    except IndexError:
                        self.initial[field_name] = ""

    class Meta:
        model   = CashDepositMember
        exclude = ['member', 'deposit_field', 'amount']

    def save(self):
        member_instance     = self.slug
        room_instance       = self.request.user.membership.room
        membership_cross_check = Membership.objects.filter(
            slug=self.slug,
            room=room_instance
        )
        if membership_cross_check.exists():
            maintainer_filter = Membership.objects.filter(
                Q(role=2),
                user=self.request.user,
                room=room_instance
            )
            member_objects = Membership.objects.filter(slug=member_instance)
            if member_objects.exists():
                member = Membership.objects.get(slug=member_instance)
                if maintainer_filter.exists():
                    now                 = datetime.datetime.now()
                    for fields in self.cleaned_data:
                        deposit_field_filter = CashDepositField.objects.filter(title=fields)
                        if deposit_field_filter.exists():
                            deposit_field = CashDepositField.objects.get(title=fields, room=room_instance)
                            value = self.cleaned_data.get(fields)
                            member_deposit_filter = CashDepositMember.objects.filter(
                                member=member, deposit_field = deposit_field, created_at__month=now.month, created_at__year=now.year
                            )
                            if member_deposit_filter.exists():
                                member_deposit_filter.update(
                                    amount = value
                                )
                            else:
                                CashDepositMember.objects.get_or_create(
                                    member = member,
                                    deposit_field = deposit_field,
                                    amount = value
                                )
                    messages.add_message(self.request, messages.SUCCESS,
                    "Cost Deposit Fields allocated successfully !")
                else:
                    messages.add_message(self.request, messages.WARNING,
                    "Something went wrong !")
        else:
            instance_user   = self.request.user
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
