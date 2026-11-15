from django.urls import path

from . import views

app_name = 'war'

urlpatterns = [
    path('', views.index, name='index'),
    path('start/', views.start, name='start'),
    path('fights/', views.fights, name='fights'),
    path('fights/<int:external_id>/', views.fight_detail, name='fight_detail'),
    path('simulate/', views.simulate, name='simulate'),
    path('simulate/run/', views.simulate_run, name='simulate_run'),
    path('simulate/reset/', views.simulate_reset, name='simulate_reset'),
]
