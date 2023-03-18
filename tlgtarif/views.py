from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.db import connection, DatabaseError

from datetime import datetime
import logging

from .models import Country, TlgTarifCountry, TlgTarif
from .tcalc import TCalc, TypeDelivery, TypeNotification, TypeLux


file_log = logging.getLogger("fileLogger")

CHECK_PARAM_LIST = [
    "lux",
    "luxv",
    "notif",
    "notifurg",
    "radioord",
    "radiourg",
    "radiopost",
    "radiobox",
    "todate",
    "service",
]


def check_url_param_bool(param):
    """проверка значения параметра из набра 'true', 'false', нет параметра"""
    if param in ("true", "false", None):
        return True

    return False


def import_test_tarif(request):
    refer = request.META.get("HTTP_REFERER")

    try:
        with connection.cursor() as cursor:
            query = """
                INSERT INTO `tlgtarif_country` (`id`, `name_country`, `delivery_box_bool`, `delivery_post_bool`, 
                                                `lux_ordinary_bool`, `lux_visual_bool`, `notification_ordinary_bool`, 
                                                `notification_urgent_bool`, `todate_bool`) 
                VALUES
                (1, 'Армения', 0, 1, 1, 0, 0, 0, 1),
                (2, 'Беларусь', 0, 1, 1, 0, 0, 0, 1),
                (3, 'Азербайджан', 0, 1, 1, 0, 0, 0, 1),
                (4, 'Грузия', 0, 1, 0, 0, 0, 0, 0),
                (5, 'Кыргызстан', 0, 1, 1, 0, 0, 0, 1),
                (6, 'Казахстан', 0, 1, 1, 0, 0, 0, 1),
                (7, 'Латвия', 0, 1, 1, 0, 0, 0, 1),
                (8, 'Литва', 0, 1, 1, 0, 0, 0, 0),
                (9, 'Молдова', 0, 1, 1, 0, 0, 0, 1),
                (10, 'Таджикистан', 0, 1, 0, 0, 0, 0, 0),
                (11, 'Туркменистан', 0, 1, 1, 0, 0, 0, 1),
                (12, 'Узбекистан', 0, 1, 1, 0, 0, 0, 1),
                (13, 'Украина', 0, 1, 1, 0, 0, 0, 1),
                (14, 'Эстония', 0, 1, 1, 0, 0, 0, 1);
            """
            cursor.execute(query)

            query = """
                INSERT INTO `tlgtarif_tlgtarifcountry` (`id`, `date_begin`, `date_end`, `word_ordinary`, 
                                                        `word_urgent`, `country_id`) 
                VALUES
                (1, '2018-12-31 21:00:00.000000', '2020-03-31 20:59:00.000000', 10, 20, 1),
                (2, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:00.000000', 33.6, 67.2, 1),
                (3, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:00.000000', 22.8, 45.6, 2),
                (4, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:59.000000', 30, 60, 3),
                (5, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:59.000000', 30, 60, 4),
                (6, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:00.000000', 22.8, 45.6, 5),
                (7, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:00.000000', 30, 60, 6),
                (8, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:00.000000', 39.6, 79.2, 7),
                (9, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:59.000000', 39.6, 79.2, 8),
                (10, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:59.000000', 30, 60, 9),
                (11, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:59.000000', 22.8, 45.6, 10),
                (12, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:59.000000', 22.8, 45.6, 11),
                (13, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:00.000000', 22.8, 45.6, 12),
                (14, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:59.000000', 30, 60, 13),
                (15, '2020-03-31 21:00:00.000000', '2028-12-01 20:59:00.000000', 23, 46, 14),
                (16, '2018-12-31 21:00:00.000000', '2020-03-31 20:59:00.000000', 10, 20, 2),
                (17, '2019-03-31 21:00:00.000000', '2019-12-01 20:59:00.000000', 23.05, 46.01, 14),
                (18, '2019-03-31 21:00:00.000000', '2019-11-30 20:59:00.000000', 22.81, 45.6, 12);
            """
            cursor.execute(query)

            query = """
                INSERT INTO `tlgtarif_tlgtarif` (`id`, `date_begin`, `date_end`, `delivery_ordinary`, `delivery_urgent`, 
                                                `delivery_post`, `delivery_box`, `word_ordinary`, `word_urgent`, 
                                                `notification_ordinary`, `notification_urgent`, `lux_ordinary`, 
                                                `lux_visual`, `todate`, `nds_percent`) 
                VALUES
                (1, '2022-09-30 21:00:00.000000', '2022-12-21 20:59:00.000000', 
                        47.3, 64.9, 64.9, 47.3, 4.4, 6.25, 165, 220, 21, 63, 25, 20),
                (2, '2021-05-31 21:00:00.000000', '2022-09-30 21:00:00.000000', 
                        43, 59, 59, 43, 4, 5.7, 150, 200, 21, 63, 25, 20),
                (3, '2022-12-21 21:00:00.000000', '2029-10-31 20:59:00.000000', 
                        47.3, 64.9, 64.9, 47.3, 4.4, 6.25, 165, 220, 22, 63, 25, 20);
            """
            cursor.execute(query)
    except DatabaseError as e:
        return render(
            request, "tlg/error.html", {"err_str": "ошибка загрузки данных : " + str(e)}
        )

    return HttpResponseRedirect(refer)


def calculator(request):
    country_list = []
    for country in Country.objects.all():
        country_list.append(country.name_country)

    context = {
        "date": datetime.today().strftime("%Y-%m-%d"),
        "country_list": country_list,
    }
    return render(request, "tlgtarif/calculator.html", context)


def tcalc(request):
    alarm = ""

    if request.GET.get("numword"):
        try:
            numword = int(request.GET.get("numword"))
        except:
            numword = 0
            alarm = "неправильное значение параметра 'numword' : " + request.GET.get(
                "numword"
            )
    else:
        numword = 0

    country = request.GET.get("country")
    datetlg = request.GET.get("date")

    tc = TCalc(datetlg, n_word=numword, country=country)

    if request.GET.get("radiourg") == "true":
        tc.set_type_delivery(TypeDelivery.URGENT)
    elif request.GET.get("radiopost") == "true":
        tc.set_type_delivery(TypeDelivery.POSTZ)
    elif request.GET.get("radiobox") == "true":
        tc.set_type_delivery(TypeDelivery.ABOX)

    if request.GET.get("notif") == "true":
        tc.set_type_notification(TypeNotification.ORD_NOTIFICATION)
    elif request.GET.get("notifurg") == "true":
        tc.set_type_notification(TypeNotification.URG_NOTIFICATION)

    if request.GET.get("lux") == "true":
        tc.set_type_lux(TypeLux.ORD_LUX)
    elif request.GET.get("luxv") == "true":
        tc.set_type_lux(TypeLux.VIS_LUX)

    if request.GET.get("service") == "true":
        tc.set_type_service(True)

    if request.GET.get("todate") == "true":
        tc.set_type_todate(True)

    for u_param in CHECK_PARAM_LIST:
        if not check_url_param_bool(request.GET.get(u_param)):
            tc.alarm = "неправильное значение параметра '{}' : {}".format(
                u_param, request.GET.get(u_param)
            )

    if len(alarm):
        tc.alarm = alarm

    if (request.GET.get("notif") == "true") and (request.GET.get("notifurg") == "true"):
        tc.alarm = "нельзя выбирать одновременно notif и notifurg"

    if (request.GET.get("lux") == "true") and (request.GET.get("luxv") == "true"):
        tc.alarm = "нельзя выбирать одновременно lux и luxv"

    if (
        (request.GET.get("radioord") == "false")
        and (request.GET.get("radiourg") == "false" or not request.GET.get("radiourg"))
        and (
            request.GET.get("radiopost") == "false" or not request.GET.get("radiopost")
        )
        and (request.GET.get("radiobox") == "false" or not request.GET.get("radiobox"))
    ):
        tc.alarm = "должен быть выбран хотя бы один из radioord, radiobox, radiopost и radiourg"
    elif (request.GET.get("radioord") == "true") + (  # выбрано более одного параметра
        request.GET.get("radiourg") == "true"
    ) + (request.GET.get("radiopost") == "true") + (
        request.GET.get("radiobox") == "true"
    ) > 1:
        tc.alarm = (
            "нельзя выбирать одновременно radioord, radiobox, radiopost и radiourg"
        )

    return JsonResponse(
        {
            "cost_service": "{:.2f}".format(tc.cost_service),
            "cost_todate": "{:.2f}".format(tc.cost_todate),
            "cost_lux": "{:.2f}".format(tc.cost_lux),
            "cost_notif": "{:.2f}".format(tc.cost_notification),
            "cost_deliv": "{:.2f}".format(tc.cost_delivery),
            "cost_word": "{:.2f}".format(tc.cost_word),
            "cost_summ": "{:.2f}".format(tc.cost),
            "cost_nds": "{:.2f}".format(tc.cost_nds),
            "errorAlert": tc.alarm,
        }
    )


def tlist(request):
    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    file_log.debug(f"{remote_ip} -> {query_str}")
    sng_tarif = []
    datetlg = (
        request.GET.get("date")
        if request.GET.get("date")
        else datetime.today().strftime("%Y-%m-%d")
    )
    try:
        dt = datetime.strptime(datetlg, "%Y-%m-%d")
    except ValueError as e:
        return render(
            request,
            "tlg/error.html",
            {"err_str": "неправильный формат даты : " + str(e)},
        )

    try:
        ttar = TlgTarif.objects.filter(date_begin__lte=dt, date_end__gt=dt)[0]

        for ttar_country in TlgTarifCountry.objects.filter(
            date_begin__lte=dt, date_end__gt=dt
        ).order_by("country__name_country"):
            sng_tarif.append(
                [
                    ttar_country.country,
                    ttar_country.word_ordinary,
                    ttar_country.word_urgent,
                ]
            )
    except IndexError as e:
        file_log.error(f"{remote_ip} -> {query_str} -> !!! тариф не найден ({e})")
        return render(request, "tlg/error.html", {"err_str": "тариф не найден"})

    context = {"date": datetlg, "rus_tarif": ttar, "sng_tarif": sng_tarif}
    return render(request, "tlgtarif/tlist.html", context)
