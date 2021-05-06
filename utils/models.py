from django.db import models
from accounts.models import UserProfile

class Notification(models.Model):
    sender = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='notification_sender', null=True, blank=True, verbose_name=('sender')
    )
    receiver = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='notification_receiver', null=True, blank=True, verbose_name=('receiver')
    )
    slug            = models.SlugField(blank=True, unique=True, verbose_name=('slug'))
    category        = models.CharField(max_length=50, null=True, blank=True, verbose_name=('category'))
    notify_type     = models.CharField(max_length=100, verbose_name=('notification type'))
    identifier      = models.CharField(max_length=200, null=True, blank=True, verbose_name=('identifier'))
    room_identifier = models.CharField(max_length=200, null=True, blank=True, verbose_name=('room identifier'))
    counter         = models.PositiveSmallIntegerField(default=1, verbose_name=('counter'))
    message         = models.CharField(max_length=200, null=True, blank=True, verbose_name=('message'))
    created_at      = models.DateTimeField(auto_now_add=True, verbose_name=('created at'))
    updated_at      = models.DateTimeField(auto_now=True, verbose_name=('updated at'))

    class Meta:
        verbose_name        = "Notification"
        verbose_name_plural = "Notifications"
        ordering            = ["updated_at"]

    def __str__(self):
        return self.notify_type

