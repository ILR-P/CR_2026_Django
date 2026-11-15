from django.contrib import admin
from django.urls import path
from army import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('simulate', views.simulate),
    path('simulate/', views.simulate),
]