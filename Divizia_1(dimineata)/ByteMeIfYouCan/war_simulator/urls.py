from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='unit_all', permanent=False), name='home'),
    path('unit', views.unit_create, name='unit_create_no_slash'),
    path('unit/', views.unit_create, name='unit_create'),
    path('unit/all', views.unit_all, name='unit_all_no_slash'),
    path('unit/all/', views.unit_all, name='unit_all'),
    path('unit/clear-data/', views.clear_game_data, name='clear_game_data'),
    path('unit/<int:unit_id>', views.unit_detail, name='unit_detail_no_slash'),
    path('unit/<int:unit_id>/', views.unit_detail, name='unit_detail'),
    path('unit/<int:unit_id>/heal', views.unit_heal, name='unit_heal_no_slash'),
    path('unit/<int:unit_id>/heal/', views.unit_heal, name='unit_heal'),
]
