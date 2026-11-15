from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_units, name='home'),
    path('unit', views.add_unit, name='add_unit'),
    path('unit/all', views.all_units, name='all_units'),
    path('unit/<int:unit_id>', views.unit_detail, name='unit_detail'),
    path('unit/<int:unit_id>/heal', views.heal_unit, name='heal_unit'),
    path('unit/<int:unit_id>/delete', views.delete_unit, name='delete_unit'),
    path('fight/simulate', views.simulate_fight, name='simulate_fight'),
]