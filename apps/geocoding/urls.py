from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import GeocodingViewSet

app_name = "geocoding"

router = DefaultRouter()
router.register(r"", GeocodingViewSet, basename="geocoding")

urlpatterns = [
    path("", include(router.urls)),
]
