from django.urls import path

from . import views

urlpatterns = [
    path("unit", views.unit_create, name="unit_create"),
    path("unit/all", views.unit_list, name="unit_list"),
    path("unit/<int:pk>", views.unit_detail, name="unit_detail"),
    path("unit/<int:pk>/heal", views.unit_heal, name="unit_heal"),
    path("fight/simulate", views.simulate, name="simulate"),
    path("fight/<int:pk>", views.fight_detail, name="fight_detail"),
]
