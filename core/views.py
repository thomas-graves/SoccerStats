"""
Views for the core app.

This file contains request handlers for the app's pages.
For now, it includes a simple homepage view that renders
the first HTML template for the project.
"""

from django.shortcuts import render


def home(request):
    """Render the homepage template for the Soccer Stats app."""
    return render(request, "core/home.html")
