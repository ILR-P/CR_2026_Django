from django.urls import path
from . import views

urlpatterns = [
    path('', views.add_unit, name='add_unit'),          # Cerința 1: /unit
    path('all/', views.list_units, name='list_units'),  # Cerința 2: /unit/all
    path('<int:unit_id>/', views.unit_detail, name='unit_detail'), # Cerința 2 și 4a
]