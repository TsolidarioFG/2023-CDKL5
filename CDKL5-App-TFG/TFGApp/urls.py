"""TFGApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import handler404, handler500, handler400

from login.views import error_404_view, error_500_view, error_400_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('manage/', include('dataManagement.urls')),
    path('foro/', include('foro.urls')),
    path('notices/', include('notificaciones.urls')),
    path('', include('login.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = error_400_view
handler404 = error_404_view
handler500 = error_500_view