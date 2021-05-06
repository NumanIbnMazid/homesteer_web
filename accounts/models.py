from django.db import models
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from .utils import time_str_mix_slug, upload_image_path
from django.contrib.auth.models import User

class UserQuerySet(models.query.QuerySet):
    def active(self):
        return UserProfile.objects.filter(user__is_active=True)
    def latest(self):
        return UserProfile.objects.filter(user__is_active=True).order_by('-user__date_joined')
    def search(self, query):
        lookups = (
                Q(user__username__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(contact__icontains=query) |
                Q(gender__icontains=query) |
                Q(about__icontains=query) |
                Q(address__icontains=query) |
                Q(facebook__icontains=query) |
                Q(linkedin__icontains=query) |
                Q(website__icontains=query)
                )
        return self.filter(lookups).distinct()

class UserManager(models.Manager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)
    # def all(self):
    #     return self.get_queryset().active()
    # def get_by_id(self, id):
    #     qs = self.get_queryset().filter(id=id)
    #     if qs.count() == 1:
    #         return qs.first()
    #     return None
    # def search(self, query):
    #     return self.get_queryset().active().search(query)

class UserProfile(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    OTHERS = 'O'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHERS, 'Others'),
    )
    REGULAR         = 0
    PREMIUM         = 1
    TYPE_CHOICES    = (
        (REGULAR, 'Regular'),
        (PREMIUM, 'Premium')
    )
    user            = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True, related_name='profile', verbose_name=('user'))
    slug            = models.SlugField(
        blank=True, unique=True, verbose_name=('slug'))
    user_type       = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES, default=0, null=True, blank=True, verbose_name=('user_type'))
    contact         = models.CharField(
        max_length=14, blank=True, null=True, verbose_name=('contact'))
    gender          = models.CharField(
        choices=GENDER_CHOICES, max_length=2, null=True, blank=True, verbose_name=('gender'))
    image           = models.ImageField(
        upload_to=upload_image_path, null=True, blank=True, verbose_name=('image'))
    about           = models.TextField(
        null=True, blank=True, max_length=150, verbose_name=('about'))
    address        = models.CharField(
        null=True, blank=True, max_length=77, verbose_name=('address'))
    facebook        = models.CharField(
        null=True, blank=True, max_length=300, verbose_name=('facebook'))
    linkedin        = models.CharField(
        null=True, blank=True, max_length=300, verbose_name=('linkedin'))
    website        = models.CharField(
        null=True, blank=True, max_length=300, verbose_name=('website'))
    updated_at      = models.DateTimeField(auto_now=True, null=True, verbose_name=('updated at'))

    objects = UserManager()

    class Meta:
        verbose_name        = ("User Profile")
        verbose_name_plural = ("User Profiles")
        ordering            = ["-user__date_joined"]

    def username(self):
        return self.user.username

    def get_username(self):
        if self.user.first_name or self.user.last_name:
            name = self.user.get_full_name()
        else:
            name = self.user.username
        return name

    def get_smallname(self):
        if self.user.first_name or self.user.last_name:
            name = self.user.get_short_name()
        else:
            name = self.user.username
        return name

    def __str__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return reverse("profile_public", kwargs={"slug": self.slug})

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    username        = instance.username.lower()
    slug_binding    = username+'-'+time_str_mix_slug()
    if created:
        UserProfile.objects.create(user=instance, slug=slug_binding)
    instance.profile.save()
