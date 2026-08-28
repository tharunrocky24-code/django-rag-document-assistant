from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view, dashboard_view

urlpatterns = [
    # Root & Dashboard
    path('', home_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),

    # Admin
    path('admin/', admin.site.urls),

    # Web Template Views (HTML UI)
    path('accounts/', include('accounts.urls')),
    path('documents/', include('documents.urls')),
    path('chat/', include('chat.urls')),

    # REST APIs (JSON endpoints)
    path('api/', include('config.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
