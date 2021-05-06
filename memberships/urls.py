from django.urls import path
from .views import (
    member_request_create, 
    member_request_confirm,
    member_request_delete,
    member_request_delete_all,
    member_delete,
    MemberUpdateView
    )

urlpatterns = [
    path('request/<slug>/', member_request_create, name='member_request_create'),
    path('request/<slug>/confirm/', member_request_confirm, name='member_request_confirm'),
    path('request/<slug>/delete/', member_request_delete, name='member_request_delete'),
    path('request/<slug>/delete/all/', member_request_delete_all, name='member_request_delete_all'),
    path('<slug>/delete/', member_delete, name='member_delete'),
    path('<slug>/update/', MemberUpdateView.as_view(), name='member_update'),
]
