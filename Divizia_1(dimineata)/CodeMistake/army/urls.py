from django.urls import path
from . import views

urlpatterns = [
    path('unit', views.add_unit, name='add_unit'),
]