from django.urls import path

from . import views

urlpatterns = [
    path("unit", views.unit_add, name="unit-add"),
    path("unit/", views.unit_add),
    path("unit/all", views.unit_all, name="unit-all"),
    path("unit/all/", views.unit_all),
    path("unit/simulate", views.unit_simulate, name="unit-simulate"),
    path("unit/<int:pk>", views.unit_detail, name="unit-detail"),
    path("unit/<int:pk>/", views.unit_detail),
    path("unit/<int:pk>/heal", views.unit_heal, name="unit-heal"),
]
