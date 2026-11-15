from django.urls import path
from . import views

urlpatterns = [
    path('unit', views.add_unit, name='add_unit'),
    path('unit/all', views.all_units, name='all_units'),
    path('unit/<int:unit_id>', views.unit_detail, name='unit_detail'),
    path('unit/<int:unit_id>/heal', views.heal_unit, name='heal_unit'),
]
