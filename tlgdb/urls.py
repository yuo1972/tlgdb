from django.contrib import admin
from django.urls import include, path
from rest_framework.schemas import get_schema_view


urlpatterns = [
    path("admin/", admin.site.urls),
    path("tlg/", include("tlg.urls")),
    path("tlgtarif/", include("tlgtarif.urls")),
    path("reestr/", include("reestr.urls")),
    path(
        "openapi/",
        get_schema_view(
            title="Studying", description="API for all things …", version="1.0.0"
        ),
        name="openapi-schema",
    ),
]
