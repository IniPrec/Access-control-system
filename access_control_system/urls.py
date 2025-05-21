"""
URL configuration for access_control_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views # Imports views directly

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    
    # API routes
    path('api/', include('core.urls')), # This is for API and frontend routes

    # Frontend templates views
    path('users/', core_views.user_list, name='user-list'),
    path('logs/', core_views.access_log_list, name='access-log-list'),

    # Login views
    path('login/', core_views.login_view, name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)