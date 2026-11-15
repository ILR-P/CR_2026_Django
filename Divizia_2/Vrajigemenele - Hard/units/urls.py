from django.urls import path

from . import views

urlpatterns = [
    path("unit", views.unit_create, name="unit-create"),
    path("unit/", views.unit_create),
    path("unit/all", views.unit_list, name="unit-all"),
    path("unit/<int:pk>", views.unit_detail, name="unit-detail"),
    path("unit/<int:pk>/heal", views.unit_heal, name="unit-heal"),
]
