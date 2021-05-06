from django.urls import path, include
from .views import UserProfileView, UserProfileUpdateView, UserPublicProfileView, UserListView

urlpatterns = [
    path('', include('allauth.urls')),
    path('user/all/', UserListView.as_view(), name='user_list'),
    path('user/<slug>/profile/', UserProfileView.as_view(), name='profile'),
    path('user/<slug>/update/', UserProfileUpdateView.as_view(), name='profile_update'),
    path('user/<slug>/public/profile/', UserPublicProfileView.as_view(), name='profile_public'),
]
