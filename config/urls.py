from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/account/', include('account.urls')),
    path('api/club/', include('club.urls')),
    path('api/member/', include('member.urls')),
    path('api/core/', include('core.urls')),
]
