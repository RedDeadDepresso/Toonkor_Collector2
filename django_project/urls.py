"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from toonkor_collector2 import views
from toonkor_collector2.api import app


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.LibraryView.as_view(), name='index'),
    path('toonkor_collector2/', include('toonkor_collector2.urls')),
    path("api/", app.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
