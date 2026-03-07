"""
URL configuration for config project.


This file connects the top-level URL patterns for the entire site.
It includes the Django admin route and delegates the homepage route
to the core app.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

urlpatterns = [
    # Admin site route.
    path("admin/", admin.site.urls),

    # Include the core app's URL patterns at the site root.
    path("", include("core.urls")),
]