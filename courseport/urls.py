"""
URL configuration for courseport project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include, re_path
from django.views.static import serve
from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent

urlpatterns = [
    path('', include('upload.urls')),
    path('admin/', admin.site.urls),
    re_path(r'^site/(?P<path>.*)$', serve,
        {'document_root': BASE_DIR / 'site',
         'show_indexes': True},
        name='site_path'
    ),
    path('favicon.ico', serve, {
            'path': 'favicon.ico',
            'document_root': os.path.join(BASE_DIR, 'site'),
        }
    ),
]
