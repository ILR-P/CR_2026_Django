from django.urls import path

from . import views

urlpatterns = [
    path("status", views.draft_status),
]
