from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home, PolicyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('policy/', PolicyView.as_view(), name='policy'),
    path('account/', include('accounts.urls')),
    path('rooms/', include(('rooms.urls', 'rooms'), namespace='rooms')),
    path('member/', include(('memberships.urls', 'memberships'), namespace='memberships')),
    path('tracker/', include(('tracker.urls', 'tracker'), namespace='tracker')),
    path('search/', include(("search.urls", "search"), namespace="search")),
    path('utils/', include(("utils.urls", "utils"), namespace="utils")),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)