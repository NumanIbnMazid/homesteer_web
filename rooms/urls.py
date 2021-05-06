from django.urls import path
from .views import (
    RoomCreateView, 
    RoomUpdateView, 
    RoomListView, 
    RoomDetailView,
    RoomDeleteView,
    ManagerialSettingUpdateView
)

urlpatterns = [
    path('create/', RoomCreateView.as_view(), name='room_create'),
    path('<slug>/update/', RoomUpdateView.as_view(), name='room_update'),
    path('all/', RoomListView.as_view(), name='room_list'),
    path('<slug>/detail/', RoomDetailView.as_view(), name='room_detail'),
    path('<slug>/delete/', RoomDeleteView.as_view(), name='room_delete'),
    path('managerial/settings/update/', ManagerialSettingUpdateView.as_view(), name='managerial_setting')
]
