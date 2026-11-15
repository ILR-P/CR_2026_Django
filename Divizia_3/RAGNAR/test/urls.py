from django.urls import path
from . import views

urlpatterns = [
    path('unit', views.add_unit, name='add_unit'),
    path('unit/all', views.unit_list, name='unit_list'),
    path('unit/<int:unit_id>', views.unit_detail, name='unit_detail'),
    path('unit/<int:unit_id>/heal', views.heal_unit, name='heal_unit'),
    path('fight/simulate', views.simulate_fight_view, name='simulate_fight'),
    path('fight/result/<int:fight_id>', views.fight_result_view, name='fight_result'),
]