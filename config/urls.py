from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/account/', include('account.urls')),
    path('api/club/', include('club.urls')),
    path('api/member/', include('member.urls')),
    path('api/core/', include('core.urls')),
    path('api/activity_log/', include('activity_log.urls')),
    path('api/event/', include('event.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
