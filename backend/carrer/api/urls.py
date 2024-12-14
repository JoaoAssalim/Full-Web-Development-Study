from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.carrer.api.views import CarrerViewSet, CarrerFileUpload

router = DefaultRouter()
router.register(r'carrer', CarrerViewSet, basename='carrer')

urlpatterns = [
    path("", include(router.urls)),
    path("upload", CarrerFileUpload.as_view(), name="upload"),
]