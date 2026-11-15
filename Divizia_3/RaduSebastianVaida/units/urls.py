
from django.urls import path
from . import views

urlpatterns = [
    path("", views.add_unit, name="add_unit"),

    path("all/", views.all_units, name="all_units"),

    path(
        "<int:unit_id>/",
        views.unit_details,
        name="unit_details"
    ),

    path(
        "<int:unit_id>/heal/",
        views.heal_unit,
        name="heal_unit"
    ),

    path(
        "fight/",
        views.simulate_fight,
        name="simulate_fight"
    ),
]
