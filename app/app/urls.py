"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from .settings import _APP_PREFIX, APP_PREFIX
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    # path('admin/', admin.site.urls),
    path(f'{_APP_PREFIX}', include('ui.urls')),
    path(f'{APP_PREFIX}api/', include('rest.urls')),
    path(f'{APP_PREFIX}accounts/', include('django.contrib.auth.urls')),
    path(f'{APP_PREFIX}admin/', admin.site.urls),
    path(f'select2/', include('django_select2.urls')),

]

urlpatterns += staticfiles_urlpatterns()

handler404 = 'ui.views.view_404'