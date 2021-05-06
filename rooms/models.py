from django.db import models
from django.urls import reverse
from django.conf import settings
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver

class RoomQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    def privacy_public(self):
        return self.filter(privacy=0)
    # def privacy_members(self):
    #     return self.filter(privacy=1)
    def privacy_secret(self):
        return self.filter(privacy=1)
    def latest(self):
        return self.filter().order_by('-created_at')
    def search(self, query):
        lookups = (Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(creator__username__icontains=query) |
                Q(creator__first_name__icontains=query) |
                Q(creator__last_name__icontains=query) |
                Q(creator__email__icontains=query)
                )
        return self.filter(lookups).distinct()

class RoomManager(models.Manager):
    def get_queryset(self):
        return RoomQuerySet(self.model, using=self._db)
    def all(self):
        return self.get_queryset().active()
    def get_by_id(self, id):
        qs  = self.get_queryset().filter(id=id)
        if qs.count() == 1:
            return qs.first()
        return None
    def search(self, query):
        return self.get_queryset().active().privacy_public().search(query)

class Room(models.Model):
    PUBLIC  = 0
    SECRET  = 1
    PRIVACY_CHOICES = (
        (PUBLIC, 'Public'),
        (SECRET, 'Secret')
    )
    title       = models.CharField(max_length=50, verbose_name=('title'))
    slug        = models.SlugField(blank=True, unique=True, verbose_name=('slug'))
    is_active   = models.BooleanField(default=True, verbose_name=('is_active'))
    privacy     = models.PositiveSmallIntegerField(
        choices=PRIVACY_CHOICES, default=0, verbose_name=('privacy')
    )
    description = models.TextField(null=True, blank=True, max_length=250, verbose_name=('description'))
    creator     = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True, related_name='creator', verbose_name=('creator')
    )
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name=('created at'))
    updated_at  = models.DateTimeField(auto_now=True, verbose_name=('updated at'))

    objects     = RoomManager()

    class Meta:
        ordering = ["-created_at"]

    def get_absolute_url(self):
        return reverse("rooms:room_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class ManagerialSetting(models.Model):
    INDIVIDUAL_MEMBER_DEPENDENT_SHOPPING  = 0
    ROOM_MANAGER_DEPENDENT_SHOPPING  = 1
    SHOPPING_TYPE_CHOICES = (
        (INDIVIDUAL_MEMBER_DEPENDENT_SHOPPING, 'INDIVIDUAL MEMBER DEPENDENT SHOPPING'),
        (ROOM_MANAGER_DEPENDENT_SHOPPING, 'ROOM MANAGER DEPENDENT SHOPPING')
    )
    room        = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='managerial_setting', verbose_name=('room')
    )
    shopping_type = models.PositiveSmallIntegerField(
        choices=SHOPPING_TYPE_CHOICES, default=0, verbose_name=('shopping type')
    )
    is_CUD_able = models.BooleanField(default=True, verbose_name=('is CUD able'))
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name=('created at'))
    updated_at  = models.DateTimeField(auto_now=True, verbose_name=('updated at'))

    class Meta:
        verbose_name        = "Managerial Setting"
        verbose_name_plural = "Managerial Settings"
        ordering            = ["-room__created_at"]

    def __str__(self):
        return self.room.title

@receiver(post_save, sender=Room)
def create_or_update_shopping_type(sender, instance, created, **kwargs):
    if created:
        ManagerialSetting.objects.create(room=instance, shopping_type=0)
