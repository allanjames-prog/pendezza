from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Custom URLs
    path("user/", include("userauths.urls")),
    path("", include("salon.urls")),
    path('booking/', include('booking.urls')),
    path('dashboard/', include('userDashboard.urls')),
    path('userauthentication/', include(('userauths.urls', 'userauths'), namespace='userauths')),

] 


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


