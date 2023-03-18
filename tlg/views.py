from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db import DatabaseError
from rest_framework import viewsets, mixins
from rest_framework.schemas.openapi import AutoSchema

from datetime import datetime, timezone, timedelta
import csv
import logging


from .models import Tlg
from .filters import TlgFilterSet
from .serializers import TlgSerializer


FILE_NAME_DB_TEST = "tlg0.csv"

file_log = logging.getLogger("fileLogger")

# def utc_to_local(utc_dt):
#     return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def list_db(request):
    date1 = ""
    inp_napr = request.GET.get("inpn") if request.GET.get("inpn") else ""
    out_napr = request.GET.get("outn") if request.GET.get("outn") else ""
    date_r = request.GET.get("date") if request.GET.get("date") else ""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса
    file_log.info(f"{remote_ip} -> {query_str}")

    data_list = Tlg.objects.filter(
        inp_chan__startswith=inp_napr, out_chan__startswith=out_napr
    )

    if date_r:
        date1 = datetime.strptime(date_r, "%Y-%m-%d")
        date2 = date1 + timedelta(hours=23, minutes=59, seconds=59)
        # data_list = Tlg.objects.filter(inp_gate_date__range=(utc_to_local(date1), utc_to_local(date2)))
        data_list = data_list.filter(inp_gate_date__range=(date1, date2))

    context = {
        "data": data_list,
        "inp_napr": inp_napr,
        "out_napr": out_napr,
        "date": date1,
    }

    return render(request, "tlg/list.html", context)


def import0():
    with open(FILE_NAME_DB_TEST, encoding="cp1251") as csv_file:
        file_reader = csv.DictReader(csv_file, delimiter=";")
        for row in file_reader:
            new_tlg = Tlg(
                un_name=row["un_name"],
                inp_gate_date=row["inp_gate_date"],
                inp_chan=row["inp_chan"],
                inp_num=row["inp_num"],
                inp_prz=row["inp_prz"],
                ref=row["ref"],
                kn=row["kn"],
                categ=row["categ"],
                fl_uved_bool=row["fl_uved_bool"],
                fl_urgent_bool=row["fl_urgent_bool"],
                pp=row["pp"],
                address=row["address"],
                subscribe=row["subscribe"],
                out_gate_date=row["out_gate_date"],
                out_chan=row["out_chan"],
                out_num=row["out_num"],
                out_prz=row["out_prz"],
            )
            new_tlg.save()


def import_test_db(request):
    refer = request.META.get("HTTP_REFERER")

    try:
        import0()
    except DatabaseError as e:
        return render(
            request, "tlg/error.html", {"err_str": "ошибка загрузки данных : " + str(e)}
        )

    return HttpResponseRedirect(refer)


class TlgViewSet(
    mixins.ListModelMixin,  # GET /tlg/api
    mixins.CreateModelMixin,  # POST /tlg/api
    mixins.RetrieveModelMixin,  # GET /tlg/api/1
    mixins.DestroyModelMixin,  # DELETE /tlg/api/1/
    mixins.UpdateModelMixin,  # PUT /tlg/api/1
    viewsets.GenericViewSet,
):

    queryset = Tlg.objects.all().order_by("inp_gate_date")
    serializer_class = TlgSerializer
    filterset_class = TlgFilterSet

    schema = AutoSchema(
        tags=["TlgList"],
        component_name="Tlg",
        operation_id_base="Tlg",
    )
