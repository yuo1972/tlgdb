from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import TlgViewSet, import_test_db, list_db


app_name = "tlg"

router = DefaultRouter()

router.register(
    prefix="api",
    viewset=TlgViewSet,
    basename="api",
)

urlpatterns = [
    path("import/", import_test_db, name="import"),
    path("list/", list_db, name="list"),
] + router.urls
