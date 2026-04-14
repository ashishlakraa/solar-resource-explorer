from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("solar-resource-detail", views.solar_resource_detail, name="solar_resource_detail"),
]
