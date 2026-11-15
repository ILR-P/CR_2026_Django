from django.contrib import admin
from django.urls import path
from arena import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('unit', views.unit_add, name='unit_add'),
    path('unit/all', views.unit_list, name='unit_list'),
    path('unit/<int:pk>', views.unit_detail, name='unit_detail'),
    path('unit/<int:pk>/heal', views.unit_heal, name='unit_heal'),
]
