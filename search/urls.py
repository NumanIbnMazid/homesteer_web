from django.urls import path
from .views import SearchRoomView

urlpatterns = [
    path('', SearchRoomView.as_view(), name="search-query"),
]