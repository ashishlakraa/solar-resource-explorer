from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SolarSiteViewSet

app_name = "solar"

router = DefaultRouter(trailing_slash=False)
router.register(r"solar", SolarSiteViewSet, basename="solar")

urlpatterns = [
    path("", include(router.urls)),
]

