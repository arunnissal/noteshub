from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import serve_frontend

urlpatterns = [
    path('admin/', admin.site.urls),                         # Django admin panel
    path('api/', include('marketplace.urls')),               # All your API endpoints
]

# Serve frontend static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Production: serve static files and frontend
    from django.views.static import serve as static_serve
    
    urlpatterns += [
        # Serve static files in production
        path('static/<path:path>', static_serve, {'document_root': settings.STATIC_ROOT}),
        # Serve frontend files - catch all non-API routes
        path('', serve_frontend, name='frontend'),
        path('<path:path>', serve_frontend, name='frontend_catch_all'),
    ]
