from django.contrib import admin

from .models import Tlg


@admin.register(Tlg)
class TlgAdmin(admin.ModelAdmin):
    change_list_template = "admin/tlg_change_list.html"

    list_display = (
        "un_name",
        "inp_gate_date",
        "inp_chan",
        "pp",
        "address",
        "subscribe",
        "out_chan",
    )
    # readonly_fields = ["timestamp_start", "timestamp_end"]
    # list_filter = ["is_done"]
    # search_fields = ("name",)
