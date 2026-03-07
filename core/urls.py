"""
URL configuration for the core app.

This file maps app-specific URL paths to the views that should handle them.
For now, it maps the site root to the basic homepage view.
"""

from django.urls import path

from .views import home

urlpatterns = [
    # Route the homepage URL to the home view.
    path("", home, name="home"),
]