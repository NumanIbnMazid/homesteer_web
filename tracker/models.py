from django.db import models
from rooms.models import Room, ManagerialSetting
from memberships.models import Membership
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from django.db.models import F, Sum


class Meal(models.Model):
    member              = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name='member_meal', verbose_name=('member')
    )
    slug                = models.SlugField(blank=True, unique=True, verbose_name=('slug'))
    meal_today          = models.DecimalField(
        decimal_places=2, max_digits=4, null=True, validators=[MinValueValidator(Decimal('0.00'))], verbose_name=('meal today')
    )
    meal_next_day       = models.DecimalField(
        decimal_places=2, max_digits=4, null=True, validators=[MinValueValidator(Decimal('0.00'))], verbose_name=('meal next day')
        )
    auto_entry          = models.BooleanField(default=True, verbose_name=('auto entry'))
    auto_entry_value    = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=4, validators=[MinValueValidator(Decimal('0.00'))], verbose_name=('auto entry value')
    )
    meal_date           = models.DateField(null=True, blank=True, verbose_name=('meal date'))
    confirmed_by        = models.ForeignKey(
        Membership, on_delete=models.CASCADE, null=True, blank=True, related_name='confirmed_by', verbose_name=('confirmed by')
    )
    created_at          = models.DateTimeField(auto_now_add=True, verbose_name=('created at'))
    updated_at          = models.DateTimeField(auto_now=True, verbose_name=('updated at'))

    class Meta:
        verbose_name        = "Meal Entry"
        verbose_name_plural = "Meal Entries"
        ordering            = ["-member__created_at"]

    def __str__(self):
        return self.member.user.username
    def get_room(self):
        return self.member.room.title
    get_room.short_description = 'Room'


class MealUpdateRequest(models.Model):
    member  = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name='member_meal_update', verbose_name=('member')
    )
    slug    = models.SlugField(blank=True, unique=True, verbose_name=('slug'))
    meal_should_be = models.DecimalField(
        decimal_places=2, max_digits=4, validators=[MinValueValidator(Decimal('0.00'))], verbose_name=('meal should be')
    )
    request_to    = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name='request_to', verbose_name=('request to')
    ) 
    created_at    = models.DateTimeField(auto_now_add=True, verbose_name=('created at'))
    updated_at    = models.DateTimeField(auto_now=True, verbose_name=('updated at'))

    class Meta:
        verbose_name        = "Meal Update Request"
        verbose_name_plural = "Meal Update Requests"
        ordering            = ["member__room"]

    def __str__(self):
        return self.member.user.username
    def get_room(self):
        return self.member.room.title
    get_room.short_description = 'Room'

class TrackerField(models.Model):
    title       = models.CharField(max_length=50, verbose_name=('title'))
    room        = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='tracker_field_room', verbose_name=('room')
    )
    slug        = models.SlugField(blank=True, unique=True, verbose_name=('slug'))
    description = models.TextField(null=True, blank=True, max_length=60, verbose_name=('description'))
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name=('created at'))
    updated_at  = models.DateTimeField(auto_now=True, verbose_name=('updated at'))

    class Meta:
        verbose_name        = "Cost Sector"
        verbose_name_plural = "Cost Sectors"
        ordering            = ["created_at"]

    def __str__(self):
        return self.title

class MemberTrack(models.Model):
    tracker_field   = models.ForeignKey(
        TrackerField, on_delete=models.CASCADE, null=True, blank=True, related_name='member_track_field', verbose_name=('cost sector')
    )
    cost            = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=7, default=0.00, validators=[MinValueValidator(Decimal('0.00'))], verbose_name=('cost')
    )
    # member          = models.ManyToManyField(Membership)
    member          = models.ForeignKey(
        Membership, null=True, blank=True, on_delete=models.CASCADE, related_name='member_track', verbose_name=('member')
    )
    created_at      = models.DateTimeField(auto_now_add=True, verbose_name=('created at'))
    updated_at      = models.DateTimeField(auto_now=True, verbose_name=('updated at'))

    class Meta:
        verbose_name        = "Member Track"
        verbose_name_plural = "Member Tracks"
        ordering            = ["-member__room__created_at"]

    def __str__(self):
        return self.member.user.username

    # def get_members(self):
    #     return "\n".join([m.user.username for m in self.member.all()])
    # get_members.short_description = 'Member'

    # def get_room(self):
    #     return "\n".join([m.user.membership.room.title for m in self.member.all()[:1]])
    # get_room.short_description = 'Room'

    def get_room(self):
        return self.member.room.title
    get_room.short_description = 'Room'


    # def get_tracker_field(self):
    #     return "\n".join([t.title for t in self.tracker_field.all()])
    # get_tracker_field.short_description = 'Tracker Field'

# class ShoppingType(models.Model):
#     INDIVIDUAL_MEMBER_DEPENDENT_SHOPPING  = 0
#     ROOM_MANAGER_DEPENDENT_SHOPPING  = 1
#     SHOPPING_TYPE_CHOICES = (
#         (INDIVIDUAL_MEMBER_DEPENDENT_SHOPPING, 'INDIVIDUAL MEMBER DEPENDENT SHOPPING'),
#         (ROOM_MANAGER_DEPENDENT_SHOPPING, 'ROOM MANAGER DEPENDENT SHOPPING')
#     )
#     room        = models.ForeignKey(
#         Room, on_delete=models.CASCADE, related_name='room_shopping_type', verbose_name=('room')
#     )
#     shopping_type = models.PositiveSmallIntegerField(
#         choices=SHOPPING_TYPE_CHOICES, default=0, verbose_name=('shopping type')
#     )
#     created_at  = models.DateTimeField(auto_now_add=True, verbose_name=('created at'))
#     updated_at  = models.DateTimeField(auto_now=True, verbose_name=('updated at'))

#     class Meta:
#         verbose_name        = "Shopping Type"
#         verbose_name_plural = "Shopping Types"
#         ordering            = ["-room__created_at"]

#     def __str__(self):
#         return self.room.title

class Shopping(models.Model):
    INDIVIDUAL  = 0
    MANAGERIAL  = 1
    SHOP_TYPE_CHOICES = (
        (INDIVIDUAL, 'INDIVIDUAL'),
        (MANAGERIAL, 'MANAGERIAL')
    )
    created_by      = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name='member_shopping', verbose_name=('created by')
    )
    item            = models.CharField(
        max_length = 50, verbose_name = ('item')
    )
    slug            = models.SlugField(blank=True, unique=True, verbose_name=('slug'))
    quantity        = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=8, validators=[MinValueValidator(Decimal('0.00'))], verbose_name=('quantity')
    )
    quantity_unit   = models.CharField(
        null=True, blank=True, max_length = 10, verbose_name = ('quantity unit')
    )
    cost            = models.DecimalField(
        decimal_places=2, max_digits=8, validators=[MinValueValidator(Decimal('0.00'))], verbose_name=('cost')
    )
    shop_type       = models.PositiveSmallIntegerField(
        choices=SHOP_TYPE_CHOICES, default=0, verbose_name=('shop type')
    )
    date            = models.DateTimeField(verbose_name=('date'))
    created_at      = models.DateTimeField(auto_now_add=True, verbose_name=('created at'))
    updated_at      = models.DateTimeField(auto_now=True, verbose_name=('updated at'))

    class Meta:
        verbose_name        = "Shopping"
        verbose_name_plural = "Shoppings"
        ordering            = ["-created_by__room__created_at"]

    def __str__(self):
        return self.item

    def get_room(self):
        return self.created_by.room.title
    get_room.short_description = 'Room'

class CashDepositField(models.Model):
    title           = models.CharField(
        null=True, max_length = 20, verbose_name = ('title')
    )
    description     = models.TextField(null=True, blank=True, max_length=60, verbose_name=('description'))
    slug            = models.SlugField(blank=True, unique=True, verbose_name=('slug'))
    room            = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='deposit_field_room', verbose_name=('room')
    )
    created_at      = models.DateTimeField(auto_now_add=True, verbose_name=('created at'))
    updated_at      = models.DateTimeField(auto_now=True, verbose_name=('updated at'))

    class Meta:
        verbose_name        = "Cash Deposit Field"
        verbose_name_plural = "Cash Deposit Fields"
        ordering            = ["-room__created_at"]

    def __str__(self):
        return self.title

class CashDepositMember(models.Model):
    deposit_field   = models.ForeignKey(
        CashDepositField, on_delete=models.CASCADE, null=True, blank=True, related_name='member_deposit_field', verbose_name=('deposit field')
    )
    amount          = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=7, default=0.00, validators=[MinValueValidator(Decimal('0.00'))], verbose_name=('amount')
    )
    member          = models.ForeignKey(
        Membership, null=True, blank=True, on_delete=models.CASCADE, related_name='member_cash_deposit', verbose_name=('member')
    )
    created_at      = models.DateTimeField(auto_now_add=True, verbose_name=('created at'))
    updated_at      = models.DateTimeField(auto_now=True, verbose_name=('updated at'))

    class Meta:
        verbose_name        = "Member Cash Deposit"
        verbose_name_plural = "Member Cash Deposits"
        ordering            = ["-member__room__created_at"]

    def __str__(self):
        return self.member.user.username

    def get_room(self):
        return self.member.room.title
    get_room.short_description = 'Room'

class TotalHolder(models.Model):
    member          = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name='member_total_holder', verbose_name=('member')
    )
    created_at      = models.DateTimeField(auto_now_add=True, verbose_name=('created at'))
    updated_at      = models.DateTimeField(auto_now=True, verbose_name=('updated at'))

    def __str__(self):
        return self.member.user.username
    
    class Meta:
        verbose_name        = "Total Holder"
        verbose_name_plural = "Total Holders"
        ordering            = ["-member__room__created_at"]

    def get_room(self):
        return self.member.room.title
    get_room.short_description = 'Room'

    def get_total_meal(self):
        now             = datetime.datetime.now()
        member_meals_filter = Meal.objects.filter(
            member=self.member, meal_date__day__lte=now.day, meal_date__month=now.month, meal_date__year=now.year
        ).only('meal_today')
        if member_meals_filter.exists():
            total = member_meals_filter.aggregate(total=Sum(F('meal_today'))).get('total',0.00)
            return total
        return 0

    def get_total_meal_room(self):
        now             = datetime.datetime.now()
        total = 0
        member_meals_filter = Meal.objects.filter(
            member__room=self.member.room, meal_date__day__lte=now.day, meal_date__month=now.month, meal_date__year=now.year
        ).only('meal_today')
        if member_meals_filter.exists():
            total = member_meals_filter.aggregate(total=Sum(F('meal_today'))).get('total',0.00)
        return total

    def get_total_cost_sector(self):
        tracker_filter = MemberTrack.objects.filter(
            member=self.member, member__room=self.member.room
        )
        if tracker_filter.exists():
            total = tracker_filter.aggregate(total=Sum(F('cost'))).get('total',0.00)
            return total
        return 0

    def get_total_cost_sector_room(self):
        total = 0
        tracker_filter = MemberTrack.objects.filter(
            member__room=self.member.room
        )
        if tracker_filter.exists():
            total = tracker_filter.aggregate(total=Sum(F('cost'))).get('total',0.00)
        return total

    def get_total_shopping(self):
        now     = datetime.datetime.now()
        total   = 0
        shopping_filter = Shopping.objects.filter(
            created_by=self.member, created_by__room=self.member.room, shop_type=0, date__month=now.month, date__year=now.year
        )
        if shopping_filter.exists():
            total = shopping_filter.aggregate(total=Sum(F('cost'))).get('total',0.00)
        return total

    def get_total_shopping_room(self):
        now     = datetime.datetime.now()
        total   = 0
        shopping_filter = Shopping.objects.filter(
            created_by__room=self.member.room, shop_type=0, date__month=now.month, date__year=now.year
        )
        if shopping_filter.exists():
            total = shopping_filter.aggregate(total=Sum(F('cost'))).get('total',0.00)
        return total

    def get_total_monthly_shopping(self):
        now     = datetime.datetime.now()
        total   = 0
        shopping_filter = Shopping.objects.filter(
            created_by__room=self.member.room, shop_type=1, date__month=now.month, date__year=now.year
        )
        if shopping_filter.exists():
            total = shopping_filter.aggregate(total=Sum(F('cost'))).get('total',0.00)
        return total

    def get_grand_total_shopping(self):
        total   = 0
        now     = datetime.datetime.now()
        shopping_type_filter = ManagerialSetting.objects.filter(
            room=self.member.room
        )
        if shopping_type_filter.exists():
            shopping_type = shopping_type_filter.first().shopping_type
            shopping_filter = Shopping.objects.filter(
                created_by__room=self.member.room, date__month=now.month, date__year=now.year
            )
            if shopping_filter.exists():
                if shopping_type == 0:
                    total = self.get_total_shopping_room() + self.get_total_monthly_shopping()
                else:
                    total = self.get_total_monthly_shopping()
        return total

    def get_deposit_total_member(self):
        now     = datetime.datetime.now()
        total   = 0
        deposit_filter = CashDepositMember.objects.filter(member=self.member, created_at__month=now.month, created_at__year=now.year)
        if deposit_filter.exists():
            total = deposit_filter.aggregate(total=Sum(F('amount'))).get('total',0.00)
        return total

    def get_deposit_total_room(self):
        now     = datetime.datetime.now()
        total   = 0
        deposit_filter = CashDepositMember.objects.filter(member__room=self.member.room, created_at__month=now.month, created_at__year=now.year)
        if deposit_filter.exists():
            total = deposit_filter.aggregate(total=Sum(F('amount'))).get('total',0.00)
        return total


@receiver(post_save, sender=Membership)
def create_or_update_total_holder(sender, instance, created, **kwargs):
    if created:
        TotalHolder.objects.create(member=instance)

@receiver(post_save, sender=CashDepositField)
def create_or_update_cash_deposit_field(sender, instance, created, **kwargs):
    if created:
        members_filter = Membership.objects.filter(room=instance.room)
        if members_filter.exists():
            for member in members_filter:
                CashDepositMember.objects.create(deposit_field=instance, member=member, amount=0)

@receiver(post_save, sender=Membership)
def create_or_update_cash_deposit_member(sender, instance, created, **kwargs):
    if created:
        deposit_fields = CashDepositField.objects.filter(room=instance.room)
        if deposit_fields.exists():
            for field in deposit_fields:
                CashDepositMember.objects.create(member=instance, deposit_field=field, amount=0)