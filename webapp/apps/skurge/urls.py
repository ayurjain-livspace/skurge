"""skurge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

urlpatterns = [
    # Event processing through config driven process
    path('api/v1/relay-event/<slug:event_name>', views.EventProcessorView.as_view(http_method_names=['post']), name='skurge-relayer'),
    # Registers an event in skurge
    path('api/v1/register-event', views.SourceEventView.as_view(http_method_names=['post']), name='register-event'),
    # Get all registered events
    path('api/v1/registered-events', views.RegisteredEventsView.as_view(http_method_names=['get']), name='get-all-registered-event'),
    # Update registered event
    # Get event along with its processors
    path('api/v1/registered-event/<int:event_id>', views.SourceEventView.as_view(http_method_names=['get', 'put']), name='get-update-registered-event'),
    # Add relay and data processor for an event
    path('api/v1/registered-event/<int:event_id>/relayer', views.RelayEventView.as_view(http_method_names=['post']), name='add-relay-processor'),
    # Update relay or data processor
    # Get relay processor along with its data processor
    path('api/v1/registered-event/<int:event_id>/relayer/<int:relayer_id>', views.RelayEventView.as_view(http_method_names=['get', 'put']),
         name='update-relay-processor')
]
