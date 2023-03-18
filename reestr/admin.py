from django.contrib import admin

from .models import Client, UserTlg, Reestr, Record


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    change_list_template = "admin/reestr_clients_change_list.html"

    list_display = (
        "code",
        "shortname",
        "fullname",
        "email",
    )


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    pass


@admin.register(UserTlg)
class UserTlgAdmin(admin.ModelAdmin):
    change_list_template = "admin/reestr_users_change_list.html"

    list_display = (
        "user",
        "fullname",
        "index_prefix",
        "billing_bool",
        "reestr_bool",
    )


@admin.register(Reestr)
class ReestrAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "usertlg",
        "fl_created",
        "fl_processed",
    )
