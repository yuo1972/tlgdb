from django.urls import include, path

from .views import (
    import_test_clients,
    import_test_users,
    select,
    add,
    list_records,
    delete,
    set_client,
    tarification,
    update_record,
    reset_record,
    update_numword,
    save_record,
    complit,
    fixed,
    change,
    billing,
    billing_on,
    billing_off,
    detail,
    detail_client,
    send_detail,
)


app_name = "reestr"

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("import_clients/", import_test_clients, name="import_clients"),
    path("import_users/", import_test_users, name="import_users"),
    path("select/", select, name="select"),
    path("add/<date>/", add, name="add"),
    path("list/<id_reestr>/", list_records, name="list"),
    path("delete/<id_reestr>/<un_tlg>/", delete, name="delete"),
    path("set_client/", set_client, name="set_client"),
    path("tarification/<id_reestr>/", tarification, name="tarification"),
    path("update_record/<id_record>/", update_record, name="update_record"),
    path("reset_record/<id_record>/", reset_record, name="reset_record"),
    path("save_record/<id_record>/", save_record, name="save_record"),
    path("update_numword/<id_record>/", update_numword, name="update_numword"),
    path("complit/<id_reestr>/", complit, name="complit"),
    path("fixed/<id_reestr>/", fixed, name="fixed"),
    path("change/<id_reestr>/", change, name="change"),
    path("billing/", billing, name="billing"),
    path("billing_on/<id_reestr>/", billing_on, name="billing_on"),
    path("billing_off/<id_reestr>/", billing_off, name="billing_off"),
    path("detail/", detail, name="detail"),
    path("detail/<client_id>/<yyyy_mm>/", detail_client, name="detail_client"),
    path("send_detail/<client_id>/<yyyy_mm>/", send_detail, name="send_detail"),
]
