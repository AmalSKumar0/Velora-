
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from users.views.auth_views import home,login_view,register_view,logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home,name="home"),
    path('auth/login/',login_view,name="login"),
    path('auth/register/',register_view,name="register"),
    path('auth/logout/',logout_view,name="logout"),

    path('users/', include('users.urls')),
    path('core/', include('core.urls')),
    path('commissions/',include('commissions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
