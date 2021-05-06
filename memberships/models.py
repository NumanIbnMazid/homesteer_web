from django.db import models
from django.conf import settings
from rooms.models import Room
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.utils import time_str_mix_slug

class Membership(models.Model):
    MEMBER      = 0
    SUPERVISOR  = 1
    MANAGER     = 2
    ROLE_CHOICES = (
        (MEMBER, 'Member'),
        (SUPERVISOR, 'Supervisor'),
        (MANAGER, 'Manager')
    )
    user            = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True, related_name='membership', verbose_name=('user')
    )
    role        = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES, default=0, verbose_name=('role'))
    room        = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='room', verbose_name=('room')
    )
    slug        = models.SlugField(unique=True, verbose_name=('slug'))
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name=('created_at'))
    updated_at  = models.DateTimeField(auto_now=True, verbose_name=('updated_at'))

    class Meta:
        verbose_name        = ("Membership")
        verbose_name_plural = ("Memberships")
        ordering            = ["-created_at"]

    def __str__(self):
        return self.user.username

class MemberRequest(models.Model):
    user            = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True, related_name='member_request', verbose_name=('user')
    )
    room        = models.ForeignKey(
        Room, on_delete=models.CASCADE, blank=True, null=True, related_name='member_request_room', verbose_name=('room')
    )
    slug        = models.SlugField(blank=True, unique=True, verbose_name=('slug'))
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name=('created_at'))
    updated_at  = models.DateTimeField(auto_now=True, verbose_name=('updated_at'))

    class Meta:
        verbose_name        = ("Member Request")
        verbose_name_plural = ("Member Requests")
        ordering            = ["-created_at"]

    def __str__(self):
        return self.user.username

    # def get_absolute_url(self):
    #     return reverse("memberships:member_request_detail", kwargs={"slug": self.slug})

def post_save_membership_create(sender, instance, created, *args, **kwargs):
    user            = instance.creator
    room            = instance
    slug_binding    = user.username.lower()+'-'+time_str_mix_slug()
    if created:
        Membership.objects.get_or_create(user=user, room=room, role=2, slug=slug_binding)
    membership, created = Membership.objects.get_or_create(user=user)
    if Membership.role is None or Membership.role == '' :
        Membership.role = 2
        Membership.save()

post_save.connect(post_save_membership_create, sender=Room)