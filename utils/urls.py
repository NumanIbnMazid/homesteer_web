from django.urls import path
from .views import (
    notification_delete,
    NotificationListView,
)

urlpatterns = [
    path('notification/<slug>/remove/', notification_delete, name='notification_delete'),
    path('notification/all/', NotificationListView.as_view(), name='notification_list')
]