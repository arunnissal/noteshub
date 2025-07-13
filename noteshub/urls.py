from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),                         # Django admin panel
    path('api/', include('marketplace.urls')),               # All your API endpoints
]

# This is for serving media files (like uploaded images/notes) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
