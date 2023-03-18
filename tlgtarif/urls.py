from django.urls import path

from .views import import_test_tarif, calculator, tcalc, tlist


app_name = "tlgtarif"
urlpatterns = [
    path("import/", import_test_tarif, name="import_tarif"),
    path("calculator/", calculator, name="calculator"),
    path("tcalc/api/", tcalc, name="tcalc"),
    path("tlist/", tlist, name="tlist"),
]
