from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db import connection, DatabaseError
from django.db.models import Sum
from django.core.mail import EmailMessage

from datetime import datetime, timedelta
import locale
import json
import csv
import os
import logging

from .models import (
    Tlg,
    Reestr,
    Client,
    Record,
    TypeNotiifcationR,
    TypeLuxR,
    TypeUrgentR,
)

from tlgtarif.tcalc import TCalc, TypeDelivery, TypeNotification, TypeLux
from tlgtarif.models import Country

from .util import (
    get_type_lux,
    get_type_notification,
    get_type_urgent,
    get_num_word,
    is_todate,
    month_rus,
    utc_to_local,
    float_comma,
    get_value_by_name,
)

locale.setlocale(locale.LC_TIME, "")

file_log = logging.getLogger("fileLogger")
console_log = logging.getLogger("consoleLogger")


def import_test_clients(request):
    refer = request.META.get("HTTP_REFERER")

    try:
        with connection.cursor() as cursor:
            query = """
                        INSERT INTO `reestr_client` (`id`, `code`, `shortname`, `fullname`, `email`) VALUES
                        (1, '00001', 'таможня', 'Южное таможенное управление', 'yura@rst.rostelemail.ru'),
                        (2, '00002', 'управление', 'Отдел управления по Ростовской области', 'upr@rst.rostelemail.ru'),
                        (3, '00101', 'занятость', 'Служба занятости РО', 'zan@rst.rostelemail.ru');
            """
            cursor.execute(query)

    except DatabaseError as e:
        return render(
            request,
            "reestr/error.html",
            {"err_str": "ошибка загрузки данных : " + str(e)},
        )

    return HttpResponseRedirect(refer)


def import_test_users(request):
    refer = request.META.get("HTTP_REFERER")

    try:
        with connection.cursor() as cursor:
            query = """
            INSERT INTO `auth_user` (`password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
            ('pbkdf2_sha256$390000$amtsXgbOBy833s8cN4Fuya$xXpfgDsUX6+Vfd3uFqrRqOBn1erFCqo/5HkpaTOw0Nw=', '2023-03-04 18:14:35.000000', 0, 'pok-2', '', '', '', 0, 1, '2023-02-27 07:31:32.000000'),
            ('pbkdf2_sha256$390000$jTgQWWzqgohfgCH4e3BtkW$6WjPlKWiMjfaozrDkFfe1mZ32tnKWKy3mzI+f1s8QdE=', '2023-03-04 17:46:05.000000', 0, 'tgn', '', '', '', 0, 1, '2023-03-03 14:00:05.000000'),
            ('pbkdf2_sha256$390000$hqAgSb587CwS1B8pHZfAPS$Ce7kAHE44RqyJXX4jXLN/ChvoZlBjhVioqXC7BOUZR4=', '2023-03-04 18:05:36.021739', 0, 'bill-1', 'Анна', 'Иванова', '', 0, 1, '2023-03-03 14:19:49.000000');
            """
            cursor.execute(query)

            query = """
            INSERT INTO `reestr_usertlg` (`index_prefix`, `billing_bool`, `fullname`, `user_id`, `reestr_bool`) VALUES
            ('623600', 0, 'Таганрог-600', (SELECT id FROM `auth_user` WHERE `username` = 'tgn'), 1),
            ('123002', 0, 'ПОК-2', (SELECT id FROM `auth_user` WHERE `username` = 'pok-2'), 1),
            ('', 1, 'отдел биллинга', (SELECT id FROM `auth_user` WHERE `username` = 'bill-1'), 0);
            """
            cursor.execute(query)

    except DatabaseError as e:
        return render(
            request,
            "reestr/error.html",
            {"err_str": "ошибка загрузки данных : " + str(e)},
        )

    return HttpResponseRedirect(refer)


def import_test_users0(request):
    refer = request.META.get("HTTP_REFERER")

    try:
        with connection.cursor() as cursor:
            query = """
            INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
            (2, 'pbkdf2_sha256$390000$amtsXgbOBy833s8cN4Fuya$xXpfgDsUX6+Vfd3uFqrRqOBn1erFCqo/5HkpaTOw0Nw=', '2023-03-04 18:14:35.000000', 0, 'pok-2', '', '', '', 0, 1, '2023-02-27 07:31:32.000000'),
            (3, 'pbkdf2_sha256$390000$jTgQWWzqgohfgCH4e3BtkW$6WjPlKWiMjfaozrDkFfe1mZ32tnKWKy3mzI+f1s8QdE=', '2023-03-04 17:46:05.000000', 0, 'tgn', '', '', '', 0, 1, '2023-03-03 14:00:05.000000'),
            (4, 'pbkdf2_sha256$390000$hqAgSb587CwS1B8pHZfAPS$Ce7kAHE44RqyJXX4jXLN/ChvoZlBjhVioqXC7BOUZR4=', '2023-03-04 18:05:36.021739', 0, 'bill-1', 'Анна', 'Иванова', '', 0, 1, '2023-03-03 14:19:49.000000');
            """
            cursor.execute(query)

            query = """
            INSERT INTO `reestr_usertlg` (`id`, `index_prefix`, `billing_bool`, `fullname`, `user_id`, `reestr_bool`) VALUES
            (1, '623600', 0, 'Таганрог-600', 3, 1),
            (2, '123002', 0, 'ПОК-2', 2, 1),
            (3, '', 1, 'отдел биллинга', 4, 0);
            """
            cursor.execute(query)

    except DatabaseError as e:
        return render(
            request,
            "reestr/error.html",
            {"err_str": "ошибка загрузки данных : " + str(e)},
        )

    return HttpResponseRedirect(refer)


def select(request):
    """формирование страницы для добавления записей в реестр"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return redirect("%s?next=%s" % (settings.LOGIN_URL, query_str))

    try:
        if not request.user.usertlg.reestr_bool:  # нет прав формировать реестры
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return render(request, "reestr/error.html", {"err_str": "нет доступа"})
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    name = request.user.usertlg.fullname

    un_name_list = []  # список телеграмм уже включенных в реестр

    legend = {
        "не выбрано": "class=table-light",
        "выбрано": "class=table-warning",
        "уже есть в реестре": "class=table-info",
    }

    dateR = request.GET.get("date")
    if not dateR:
        return render(request, "reestr/error.html", {"err_str": "не указана дата"})

    date1 = datetime.strptime(dateR, "%Y-%m-%d")
    date2 = date1 + timedelta(hours=23, minutes=59, seconds=59)

    shape_date = date1.strftime("%d ") + month_rus(date1.month) + date1.strftime(" %Y")

    r = Reestr.objects.filter(date=dateR, usertlg=request.user.usertlg)
    if r:  # реестры с этой датой уже есть
        if r[0].fl_created:  # счет сформирован - переадресация на финальную страницу
            return HttpResponseRedirect(
                reverse("reestr:complit", kwargs={"id_reestr": r[0].id})
            )

        for rec in r[0].reestr_records.all():
            un_name_list.append(rec.tlg.un_name)

        shape_correct = "добавить в реестр"
    else:  # создаем новый реестр
        shape_correct = "добавить в новый реестр"

    data_list = Tlg.objects.filter(
        inp_gate_date__range=(utc_to_local(date1), utc_to_local(date2))
    )
    data_list = data_list.filter(
        inp_chan__istartswith=request.user.usertlg.index_prefix
    )
    # data_list = data_list.filter(reduce(OR, inpnapr_query(napr)))

    for q0 in data_list:
        if q0.un_name in un_name_list:
            q0.css_class = legend["уже есть в реестре"]
        else:
            q0.css_class = ""

    context = {
        "legend": legend,
        "name": name,
        "shape_date": shape_date,
        "shape_correct": shape_correct,
        "data": data_list,
        "date": dateR,
        "request_full_path": request.get_full_path(),
    }
    return render(request, "reestr/select.html", context)


def add(request, date):
    """создание/обновление реестра, добавление в него записей (телеграмм)"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    try:
        if not request.user.usertlg.reestr_bool:  # нет прав формировать реестры
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return JsonResponse(
                {
                    "err_str": "нет доступа",
                }
            )
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    body_request = json.loads(request.body)

    try:
        r = Reestr.objects.filter(date=date, usertlg=request.user.usertlg)
        if r:  # реестры с этой датой уже есть
            if not r[0].fl_processed:  # счет не выставлен - можно исправлять (добавлять новые записи)
                only_add_to_reestr(r[0].id, body_request["records"])
                rstr_id = r[0].id
            else:
                return JsonResponse(
                    {
                        "err_str": "счет выставлен, реестр нельзя модифицировать",
                    }
                )

        else:  # создаем новый реестр
            rstr_id = only_create_reestr(
                request.user.usertlg, date, body_request["records"]
            )

    except DatabaseError as e:
        return JsonResponse(
            {
                "err_str": "create reestr : " + str(e),
            }
        )

    return JsonResponse(
        {
            "reestr_id": str(rstr_id),
        }
    )


def only_create_reestr(abon, date, records):
    rstr = Reestr(usertlg=abon, date=date, date_created=datetime.today())
    rstr.save()

    for un_rec in records:
        t = Tlg.objects.get(un_name=un_rec)

        typeNot = get_type_notification(t.address, t.fl_uved_bool)
        typeLX = get_type_lux(t.address)
        typeUrg = get_type_urgent(t.address, t.fl_urgent_bool)
        num_word = get_num_word(t.pp)
        todate = is_todate(t.address)

        t.tlg_records.create(
            typeNot=typeNot,
            typeLX=typeLX,
            typeUrg=typeUrg,
            num_word=num_word,
            todate_bool=todate,
            reestr=rstr,
        )

    return rstr.id


def only_add_to_reestr(idr, records):
    rstr = Reestr.objects.get(id=idr)

    un_name_list = []
    for rec in rstr.reestr_records.all():  # для избежания дублирования
        un_name_list.append(rec.tlg.un_name)

    for un_rec in records:
        if un_rec not in un_name_list:
            t = Tlg.objects.get(un_name=un_rec)

            typeNot = get_type_notification(t.address, t.fl_uved_bool)
            typeLX = get_type_lux(t.address)
            typeUrg = get_type_urgent(t.address, t.fl_urgent_bool)
            num_word = get_num_word(t.pp)
            todate = is_todate(t.address)

            t.tlg_records.create(
                typeNot=typeNot,
                typeLX=typeLX,
                typeUrg=typeUrg,
                num_word=num_word,
                todate_bool=todate,
                reestr=rstr,
            )


def list_records(request, id_reestr):
    """формирование страницы со списком телеграмм в реестре, выбор клиента"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return redirect("%s?next=%s" % (settings.LOGIN_URL, request.get_full_path()))

    reestr = Reestr.objects.get(id=id_reestr)

    try:
        if not request.user.usertlg.reestr_bool:  # нет прав формировать реестры
            if request.user.usertlg.billing_bool and reestr.fl_created:
                # для пользователей, могущих работать с биллингом и если реестр сформирован
                return HttpResponseRedirect(
                    reverse("reestr:complit", kwargs={"id_reestr": reestr.id})
                )
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return render(request, "reestr/error.html", {"err_str": "нет доступа"})
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    if reestr.usertlg != request.user.usertlg:  # чужой реестр
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    client_list = Client.objects.all()

    name = request.user.usertlg.fullname
    shape_date = (
        reestr.date.strftime("%d ")
        + month_rus(reestr.date.month)
        + reestr.date.strftime(" %Y")
    )

    if reestr.fl_created:  # счет сформирован - переадресация на финальную страницу
        return HttpResponseRedirect(
            reverse("reestr:complit", kwargs={"id_reestr": reestr.id})
        )

    data_list = []
    for rec in reestr.reestr_records.all():
        dl0 = rec.tlg
        dl0.client = rec.client
        dl0.record_id = rec.id

        data_list.append(dl0)

    context = {
        "data": data_list,
        "name": name,
        "shape_date": shape_date,
        "client_list": client_list,
        "date": str(reestr.date),
        "reestr_id": reestr.id,
    }

    return render(request, "reestr/list.html", context)


def delete(request, id_reestr, un_tlg):
    """удаление записей из реестра"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    try:
        if not request.user.usertlg.reestr_bool:  # нет прав формировать реестры
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return JsonResponse(
                {
                    "err_str": "нет доступа",
                }
            )
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    try:
        Reestr.objects.get(
            id=id_reestr, usertlg=request.user.usertlg
        ).reestr_records.get(tlg__un_name=un_tlg).delete()
    except DatabaseError as e:
        return JsonResponse(
            {
                "err_str": "remove Records from Reestr : " + str(e),
            }
        )

    return JsonResponse(
        {
            "result": 1,
        }
    )


def set_client(request):
    """привязка клиента к записи"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    try:
        if not request.user.usertlg.reestr_bool:  # нет прав формировать реестры
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return JsonResponse(
                {
                    "err_str": "нет доступа",
                }
            )
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента

    body_request = json.loads(request.body)
    # print(body_request["records"])

    for r in body_request["records"]:
        rr = r.split("-")
        if len(rr) != 2:
            return JsonResponse(
                {
                    "err_str": 'неверный параметр "records" : ' + r,
                }
            )
        try:
            rcrd = Record.objects.get(id=rr[0])
            if rcrd.reestr.usertlg != request.user.usertlg:
                file_log.warning(
                    f"{remote_ip} -> {query_str} -> нет доступа к записи {rr[0]}"
                )
                return JsonResponse(
                    {
                        "err_str": f"нет доступа к записи {rr[0]}",
                    }
                )

            rcrd.client = Client.objects.get(id=rr[1])
            rcrd.save()
        except DatabaseError as e:
            return JsonResponse(
                {
                    "err_str": "ошибка обновления записи в реестре : " + str(e),
                }
            )

    return JsonResponse(
        {
            "result": 1,
        }
    )


def recalculation(rec):
    """расчет стоимости телеграммы"""

    if rec.country:
        tc = TCalc(rec.tlg.inp_gate_date, n_word=rec.num_word, country=rec.country)
    else:
        tc = TCalc(rec.tlg.inp_gate_date, n_word=rec.num_word)

    match rec.typeUrg:
        case TypeUrgentR.URGENT:
            tc.set_type_delivery(TypeDelivery.URGENT)
        case TypeUrgentR.POSTZ:
            tc.set_type_delivery(TypeDelivery.POSTZ)
        case TypeUrgentR.ABOX:
            tc.set_type_delivery(TypeDelivery.ABOX)

    match rec.typeNot:
        case TypeNotiifcationR.ORD_NOTIFICATION:
            tc.set_type_notification(TypeNotification.ORD_NOTIFICATION)
        case TypeNotiifcationR.URG_NOTIFICATION:
            tc.set_type_notification(TypeNotification.URG_NOTIFICATION)

    match rec.typeLX:
        case TypeLuxR.ORD_LUX:
            tc.set_type_lux(TypeLux.ORD_LUX)
        case TypeLuxR.VIS_LUX:
            tc.set_type_lux(TypeLux.VIS_LUX)

    if rec.todate_bool:
        tc.set_type_todate(True)

    if rec.kkv_bool:
        tc.set_type_service(True)

    rec.cost_service = tc.cost_service
    rec.cost_todate = tc.cost_todate
    rec.cost_lux = tc.cost_lux
    rec.cost_notif = tc.cost_notification
    rec.cost_deliv = tc.cost_delivery
    rec.cost_word = tc.cost_word
    rec.cost = tc.cost
    rec.cost_nds = tc.cost_nds
    rec.save()

    return tc.alarm


def tarification(request, id_reestr):
    """формирование страницы с тарификацией телеграмм"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return redirect("%s?next=%s" % (settings.LOGIN_URL, request.get_full_path()))

    try:
        if not request.user.usertlg.reestr_bool:  # нет прав формировать реестры
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return render(request, "reestr/error.html", {"err_str": "нет доступа"})
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    reestr = Reestr.objects.get(id=id_reestr)

    if reestr.usertlg != request.user.usertlg:  # чужой реестр
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    if reestr.fl_created:  # счет сформирован - переадресация на финальную страницу
        return HttpResponseRedirect(
            reverse("reestr:complit", kwargs={"id_reestr": reestr.id})
        )

    name = request.user.usertlg.fullname
    shape_date = (
        reestr.date.strftime("%d ")
        + month_rus(reestr.date.month)
        + reestr.date.strftime(" %Y")
    )

    country_list = [
        "Россия",
    ]
    for country in Country.objects.all():
        country_list.append(country)

    data_list = []
    for rec in reestr.reestr_records.all():
        if rec.autocost_bool:  # если автоматический расчет - пересчитываем стоимость
            rec.alarm = recalculation(rec)

            rec.disabled = "disabled"
            rec.checked = ""
            rec.reset_hidden = ""
            rec.calculate_hidden = "hidden"
        else:
            rec.disabled = ""
            rec.checked = "checked"
            rec.reset_hidden = "hidden"
            rec.calculate_hidden = ""

        data_list.append(rec)

    context = {
        "data": data_list,
        "name": name,
        "shape_date": shape_date,
        "country_list": country_list,
        "reestr_id": id_reestr,
        "typeUrg": TypeUrgentR.choices,
        "typeNot": TypeNotiifcationR.choices,
        "typeLux": TypeLuxR.choices,
    }
    return render(request, "reestr/tarification.html", context)


def update_record(request, id_record):
    """обновление параметров записи"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    try:
        if not request.user.usertlg.reestr_bool:  # нет прав формировать реестры
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return JsonResponse(
                {
                    "err_str": "нет доступа",
                }
            )
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    record = Record.objects.get(id=id_record)

    if record.reestr.usertlg != request.user.usertlg:  # чужой реестр
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    body_request = json.loads(request.body)

    try:
        if "country" in body_request:
            if body_request["country"] == "Россия":
                record.country = None
            else:
                record.country = Country.objects.get(
                    name_country=body_request["country"]
                )
            record.save()

        if "urgent" in body_request:
            record.typeUrg = body_request["urgent"]
            record.save()

        if "notification" in body_request:
            record.typeNot = body_request["notification"]
            record.save()

        if "lux" in body_request:
            record.typeLX = body_request["lux"]
            record.save()

        if "todate" in body_request:
            record.todate_bool = body_request["todate"]
            record.save()

        if "kkv" in body_request:
            record.kkv_bool = body_request["kkv"]
            record.save()

        if "autocost" in body_request:
            record.autocost_bool = not body_request["autocost"]
            record.save()

    except ValueError as e:
        return JsonResponse(
            {
                "err_str": "неверное значение : " + str(e),
            }
        )

    except DatabaseError as e:
        return JsonResponse(
            {
                "err_str": "ошибка обновления записи в реестре : " + str(e),
            }
        )

    except:
        return JsonResponse(
            {
                "err_str": "undefined error",
            }
        )

    jret = {
        "alarm": "",
    }
    if record.autocost_bool:  # если автоматический расчет - пересчитываем стоимость
        jret["alarm"] = recalculation(record)
        jret.update(record.cost_set)
    else:
        jret.update(record.cost_set)

    return JsonResponse(jret)


def update_numword(request, id_record):
    """изменение количества слов с пересчетом стоимости"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    try:
        if not request.user.usertlg.reestr_bool:  # нет прав формировать реестры
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return JsonResponse(
                {
                    "err_str": "нет доступа",
                }
            )
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    record = Record.objects.get(id=id_record)

    if record.reestr.usertlg != request.user.usertlg:  # чужой реестр
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    body_request = json.loads(request.body)

    try:
        if "numword" in body_request:
            record.num_word = int(body_request["numword"])
            record.save()

    except ValueError as e:
        return JsonResponse(
            {
                "err_str": "неверное значение : " + str(e),
            }
        )

    except DatabaseError as e:
        return JsonResponse(
            {
                "err_str": "ошибка обновления записи в реестре : " + str(e),
            }
        )

    except:
        return JsonResponse(
            {
                "err_str": "undefined error",
            }
        )

    jret = {
        "alarm": recalculation(record),
    }
    jret.update(record.cost_set)

    return JsonResponse(jret)


def reset_record(request, id_record):
    """сброс параметров записи в исходные"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    try:
        if not request.user.usertlg.reestr_bool:  # нет прав формировать реестры
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return JsonResponse(
                {
                    "err_str": "нет доступа",
                }
            )
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    record = Record.objects.get(id=id_record)

    if record.reestr.usertlg != request.user.usertlg:  # чужой реестр
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    jret = {
        "alarm": "",
    }
    if record.autocost_bool:  # если автоматический расчет
        record.country = None
        record.typeNot = get_type_notification(record.tlg.address, record.tlg.fl_uved_bool)
        record.typeLX = get_type_lux(record.tlg.address)
        record.typeUrg = get_type_urgent(record.tlg.address, record.tlg.fl_urgent_bool)
        record.num_word = int(get_num_word(record.tlg.pp))
        record.todate_bool = is_todate(record.tlg.address)
        record.kkv_bool = False
        record.save()  #  восстановливаем исходные значения

        jret["alarm"] = recalculation(record)  #  и пересчитываем стоимость
        jret.update(record.cost_set)

    return JsonResponse(jret)


def save_record(request, id_record):
    """сохранить параметры записи, внесенные при ручной тарификации"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    try:
        if not request.user.usertlg.reestr_bool:  # нет прав формировать реестры
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return JsonResponse(
                {
                    "err_str": "нет доступа",
                }
            )
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    record = Record.objects.get(id=id_record)

    if record.reestr.usertlg != request.user.usertlg:  # чужой реестр
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    body_request = json.loads(request.body)

    try:
        if "country" in body_request:
            if body_request["country"] == "Россия":
                record.country = None
            else:
                record.country = Country.objects.get(
                    name_country=body_request["country"]
                )

        if "urgent" in body_request:
            record.typeUrg = body_request["urgent"]

        if "notification" in body_request:
            record.typeNot = body_request["notification"]

        if "lux" in body_request:
            record.typeLX = body_request["lux"]

        if "todate" in body_request:
            record.todate_bool = body_request["todate"]

        if "kkv" in body_request:
            record.kkv_bool = body_request["kkv"]

        if "numword" in body_request:
            record.num_word = int(body_request["numword"])

        if "urgdeliv" in body_request:
            record.cost_deliv = float_comma(body_request["urgdeliv"])

        if "urgword" in body_request:
            record.cost_word = float_comma(body_request["urgword"])

        if "inpnotif" in body_request:
            record.cost_notif = float_comma(body_request["inpnotif"])

        if "inplux" in body_request:
            record.cost_lux = float_comma(body_request["inplux"])

        if "inptodate" in body_request:
            record.cost_todate = float_comma(body_request["inptodate"])

        if "inpkkv" in body_request:
            record.cost_service = float_comma(body_request["inpkkv"])

        if "summ" in body_request:
            record.cost = float_comma(body_request["summ"])

        if "summnds" in body_request:
            record.cost_nds = float_comma(body_request["summnds"])

        record.save()

    except ValueError as e:
        return JsonResponse(
            {
                "err_str": "неверное значение : " + str(e),
            }
        )

    except DatabaseError as e:
        return JsonResponse(
            {
                "err_str": "ошибка обновления записи в реестре : " + str(e),
            }
        )

    except:
        return JsonResponse(
            {
                "err_str": "undefined error",
            }
        )

    return JsonResponse(
        {
            "result": 1,
        }
    )


def complit(request, id_reestr):
    """формирование финальной страницы создания реестра"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return redirect("%s?next=%s" % (settings.LOGIN_URL, request.get_full_path()))

    try:
        name = request.user.usertlg.fullname
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    reestr = Reestr.objects.get(id=id_reestr)

    if not reestr.fl_created:  # создание реестра не завершено
        stage = 1
        shape_text = "Подтвердить создание"

        if reestr.usertlg != request.user.usertlg:  # чужой реестр
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return render(request, "reestr/error.html", {"err_str": "нет доступа"})
    else:  # создание реестра завершено
        if not request.user.usertlg.billing_bool:  # нет прав работать с биллингом
            if reestr.usertlg != request.user.usertlg:  # и если чужой реестр
                file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
                return render(request, "reestr/error.html", {"err_str": "нет доступа"})

        if reestr.fl_processed:
            stage = 3
            shape_text = "Внесен в биллинговую систему"
        else:
            stage = 2
            shape_text = "Реестр создан, в биллинговую систему не внесен"

    if request.user.usertlg.billing_bool:
        fl_bill = 1  # можно нажимать "биллинговые" кнопки
    else:
        fl_bill = 0

    if request.user.usertlg.reestr_bool:
        fl_reestr = 1  # можно нажимать "реестровые" кнопки
    else:
        fl_reestr = 0

    shape_date = (
        reestr.date.strftime("%d ")
        + month_rus(reestr.date.month)
        + reestr.date.strftime(" %Y")
    )

    data_list = []
    for rec in reestr.reestr_records.all():
        data_list.append(rec)

    context = {
        "data": data_list,
        "name": name,
        "shape_date": shape_date,
        "shape_text": shape_text,
        "stage": stage,
        "reestr_id": id_reestr,
        "operator": reestr.signature,
        "fl_reestr": fl_reestr,
        "fl_bill": fl_bill,
    }
    return render(request, "reestr/complit.html", context)


def fixed(request, id_reestr):
    """зафиксировать создание реестра"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    try:
        if not request.user.usertlg.reestr_bool:  # нет прав формировать реестры
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return JsonResponse(
                {
                    "err_str": "нет доступа",
                }
            )
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    reestr = Reestr.objects.get(id=id_reestr)

    if reestr.usertlg != request.user.usertlg:  # чужой реестр
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    body_request = json.loads(request.body)

    try:
        if "operator" in body_request:
            reestr.signature = body_request["operator"]

        reestr.fl_created = True
        reestr.date_created = datetime.today()
        reestr.save()  # теперь можно выставлять счет
    except DatabaseError as e:
        return JsonResponse(
            {
                "err_str": "ошибка обновления записи в реестре : " + str(e),
            }
        )

    return JsonResponse(
        {
            "result": 1,
        }
    )


def change(request, id_reestr):
    """разрешить редактировать реестр"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    try:
        if not request.user.usertlg.reestr_bool:  # нет прав формировать реестры
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return JsonResponse(
                {
                    "err_str": "нет доступа",
                }
            )
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    reestr = Reestr.objects.get(id=id_reestr)

    if reestr.usertlg != request.user.usertlg:  # чужой реестр
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    if reestr.fl_processed:  # счет выставлен
        return JsonResponse(
            {
                "err_str": "счет выставлен, изменять нельзя",
            }
        )

    try:
        reestr.fl_created = False
        reestr.save()  # теперь можно выставлять счет
    except DatabaseError as e:
        return JsonResponse(
            {
                "err_str": "ошибка обновления записи в реестре : " + str(e),
            }
        )

    return JsonResponse(
        {
            "result": 1,
        }
    )


def billing(request):
    """формирование страницы для операций с биллинговой системой"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return redirect("%s?next=%s" % (settings.LOGIN_URL, request.get_full_path()))

    try:
        name = request.user.usertlg.fullname
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    monthB = request.GET.get("monthB")
    if not monthB:
        return render(request, "reestr/error.html", {"err_str": "не указан месяц"})

    dateB = datetime.strptime(monthB, "%Y-%m")
    month = dateB.month
    year = dateB.year

    # shape_date = month_rus(month) + ' ' + str(year)

    reestrs = Reestr.objects.filter(date__year=year, date__month=month)
    # if (request.user.usertlg.billing_bool):  # для пользователей, могущих работать с биллингом
    #     reestrs = reestrs.filter(fl_created=True)       # черновики отсеиваем
    if request.user.usertlg.reestr_bool:  # для пользователей, могущих формировать реестры
        reestrs = reestrs.filter(
            usertlg=request.user.usertlg
        )  # только реестры этого пользователя

    operator_list = set()
    for r in reestrs:
        operator_list.add(r.usertlg)

        if r.fl_processed:
            r.status = "Закрыт"
            r.tr_class = "class=table-info"
        elif r.fl_created:
            r.status = "Сформирован"
            r.tr_class = "class=table-warning"
        else:
            r.status = "Черновик"
            r.tr_class = "class=table-light"

        # if (request.user.usertlg.reestr_bool):  # для пользователей, могущих формировать реестры
        r.todo_url = reverse("reestr:list", kwargs={"id_reestr": r.id})

        # if (request.user.usertlg.billing_bool):  # для пользователей, могущих работать с биллингом
        #     r.todo_url = reverse('reestr:complit', kwargs={'id_reestr': r.id})

    context = {
        "shape_date": monthB,
        "data": reestrs,
        "operators": operator_list,
    }
    return render(request, "reestr/billing.html", context)


def billing_on(request, id_reestr):
    """поставить отметку, о том, что биллинг произведен"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    try:
        if not request.user.usertlg.billing_bool:  # нет прав на операции с биллингом
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return JsonResponse(
                {
                    "err_str": "нет доступа",
                }
            )
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    reestr = Reestr.objects.get(id=id_reestr)

    try:
        reestr.fl_processed = True
        reestr.save()  # реестр изменять больше нельзя
    except DatabaseError as e:
        return JsonResponse(
            {
                "err_str": "ошибка обновления записи в реестре : " + str(e),
            }
        )

    return JsonResponse(
        {
            "result": 1,
        }
    )


def billing_off(request, id_reestr):
    """поставить отметку, о том, что биллинг отменен"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    try:
        if not request.user.usertlg.billing_bool:  # нет прав на операции с биллингом
            file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
            return JsonResponse(
                {
                    "err_str": "нет доступа",
                }
            )
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return JsonResponse(
            {
                "err_str": "нет доступа",
            }
        )

    reestr = Reestr.objects.get(id=id_reestr)

    try:
        reestr.fl_processed = False
        reestr.save()  # реестр снова можно изменять
    except DatabaseError as e:
        return JsonResponse(
            {
                "err_str": "ошибка обновления записи в реестре : " + str(e),
            }
        )

    return JsonResponse(
        {
            "result": 1,
        }
    )


def detail(request):
    """формирование страницы со списком клиентов для вывода детализации"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return redirect("%s?next=%s" % (settings.LOGIN_URL, request.get_full_path()))

    try:
        name = request.user.usertlg.fullname
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    if not request.user.usertlg.billing_bool:  # нет прав на операции с биллингом
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    monthD = request.GET.get("monthD")
    if not monthD:
        return render(request, "reestr/error.html", {"err_str": "не указан месяц"})

    dateB = datetime.strptime(monthD, "%Y-%m")
    month = dateB.month
    year = dateB.year

    # shape_date = month_rus(month) + ' ' + str(year)

    clients = Client.objects.all()

    for client in clients:
        reestrs = Reestr.objects.filter(
            date__year=year,
            date__month=month,
            fl_processed=True,
            reestr_records__client=client,
        )
        client.summ = reestrs.aggregate(Sum("reestr_records__cost"))[
            "reestr_records__cost__sum"
        ]

    context = {
        "shape_date": monthD,
        "clients": clients,
    }
    return render(request, "reestr/detail.html", context)


def get_detail(client_id, yyyy_mm):
    """сформировать данные для вывода/отправки детализации"""

    dateB = datetime.strptime(yyyy_mm, "%Y-%m")
    month = dateB.month
    year = dateB.year

    reestrs = Reestr.objects.filter(
        date__year=year,
        date__month=month,
        fl_processed=True,
        reestr_records__client=client_id,
    )

    summ = reestrs.aggregate(Sum("reestr_records__cost"))["reestr_records__cost__sum"]
    summ_nds = reestrs.aggregate(Sum("reestr_records__cost_nds"))[
        "reestr_records__cost_nds__sum"
    ]

    records = reestrs.values(
        "reestr_records__tlg__inp_gate_date",
        "reestr_records__tlg__kn",
        "reestr_records__tlg__address",
        "reestr_records__country__name_country",
        "reestr_records__typeUrg",
        "reestr_records__typeNot",
        "reestr_records__typeLX",
        "reestr_records__num_word",
        "reestr_records__cost_word",
        "reestr_records__cost_service",
        "reestr_records__cost_todate",
        "reestr_records__cost_lux",
        "reestr_records__cost_notif",
        "reestr_records__cost_deliv",
    )

    data = []
    for rec in records:
        dict_rec = {}

        dict_rec["date"] = rec["reestr_records__tlg__inp_gate_date"]
        dict_rec["address"] = rec["reestr_records__tlg__address"]
        dict_rec["kn"] = rec["reestr_records__tlg__kn"]

        name_urgent = get_value_by_name(rec["reestr_records__typeUrg"], TypeUrgentR)
        if rec["reestr_records__country__name_country"]:
            name_country = rec["reestr_records__country__name_country"]
        else:
            name_country = "Россия"

        dict_rec["cost"] = rec["reestr_records__cost_deliv"]
        dict_rec["num"] = 1
        dict_rec["cost_name"] = Record._meta.get_field("cost_deliv").verbose_name
        dict_rec["cost_name"] += f" ({name_urgent})"
        data.append(dict_rec.copy())

        dict_rec["cost"] = rec["reestr_records__cost_word"]
        dict_rec["num"] = rec["reestr_records__num_word"]
        dict_rec["cost_name"] = Record._meta.get_field("cost_word").verbose_name
        dict_rec["cost_name"] += f" ({name_urgent})"
        dict_rec["cost_name"] += f" ({name_country})"
        data.append(dict_rec.copy())

        if float(rec["reestr_records__cost_notif"]) > 0:
            dict_rec["cost"] = rec["reestr_records__cost_notif"]
            dict_rec["num"] = 1
            dict_rec["cost_name"] = Record._meta.get_field("cost_notif").verbose_name
            dict_rec[
                "cost_name"
            ] += f" ({get_value_by_name(rec['reestr_records__typeNot'], TypeNotiifcationR)})"
            data.append(dict_rec.copy())

        if float(rec["reestr_records__cost_lux"]) > 0:
            dict_rec["cost"] = rec["reestr_records__cost_lux"]
            dict_rec["num"] = 1
            dict_rec["cost_name"] = Record._meta.get_field("cost_lux").verbose_name
            dict_rec[
                "cost_name"
            ] += f" ({get_value_by_name(rec['reestr_records__typeLX'], TypeLuxR)})"
            data.append(dict_rec.copy())

        if float(rec["reestr_records__cost_todate"]) > 0:
            dict_rec["cost"] = rec["reestr_records__cost_todate"]
            dict_rec["num"] = 1
            dict_rec["cost_name"] = Record._meta.get_field("cost_todate").verbose_name
            data.append(dict_rec.copy())

        if float(rec["reestr_records__cost_service"]) > 0:
            dict_rec["cost"] = rec["reestr_records__cost_service"]
            dict_rec["num"] = 1
            dict_rec["cost_name"] = Record._meta.get_field("cost_service").verbose_name
            data.append(dict_rec.copy())

    return (summ, summ_nds, data)


def detail_client(request, client_id, yyyy_mm):
    """формирование страницы с детализацией клиента"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return redirect("%s?next=%s" % (settings.LOGIN_URL, request.get_full_path()))

    try:
        name = request.user.usertlg.fullname
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    if not request.user.usertlg.billing_bool:  # нет прав на операции с биллингом
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    client = Client.objects.get(id=client_id)

    (client.summ, client.summ_nds, data) = get_detail(client_id, yyyy_mm)

    context = {
        "shape_date": yyyy_mm,
        "client": client,
        "data": data,
    }
    return render(request, "reestr/detail_client.html", context)


def send_detail(request, client_id, yyyy_mm):
    """отправка детализации клиенту по email"""

    remote_ip = request.META.get("REMOTE_ADDR")  # ip-адрес клиента
    query_str = request.get_full_path()  # строка запроса

    if not request.user.is_authenticated:
        file_log.warning(f"{remote_ip} -> {query_str} -> не авторизован")
        return redirect("%s?next=%s" % (settings.LOGIN_URL, request.get_full_path()))

    try:
        name = request.user.usertlg.fullname
    except:  # если у пользователя нет расширенных параметров usertlg
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    if not request.user.usertlg.billing_bool:  # нет прав на операции с биллингом
        file_log.warning(f"{remote_ip} -> {query_str} -> нет доступа")
        return render(request, "reestr/error.html", {"err_str": "нет доступа"})

    client = Client.objects.get(id=client_id)

    (summ, summ_nds, data) = get_detail(client_id, yyyy_mm)
    summ = str(summ).replace(".", ",")
    summ_nds = str(summ_nds).replace(".", ",")

    csv_filename = f"./tmp/{str(client_id)}-{yyyy_mm}.csv"

    try:
        with open(csv_filename, "w", newline="") as csvfile:
            dialect = csv.Dialect
            dialect.delimiter = ";"
            dialect.quoting = csv.QUOTE_NONE
            dialect.quotechar = ""
            dialect.lineterminator = "\r\n"

            fieldnames = ["date", "kn", "address", "cost_name", "num", "cost"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect=dialect)

            writer.writeheader()
            for d in data:
                d["cost"] = str(d["cost"]).replace(".", ",")
                writer.writerow(d)

            writer.writerow(
                {
                    "date": "",
                    "kn": "",
                    "address": "",
                    "cost_name": "Всего:",
                    "num": "",
                    "cost": summ,
                }
            )
            writer.writerow(
                {
                    "date": "",
                    "kn": "",
                    "address": "",
                    "cost_name": "Всего с НДС:",
                    "num": "",
                    "cost": summ_nds,
                }
            )

    except BaseException as e:
        return render(
            request,
            "reestr/error.html",
            {"err_str": "ошибка создания csv-файла : " + str(e)},
        )

    email = EmailMessage("Детализация счета за " + yyyy_mm)

    email.body = f"Детализация счета клиента {client.fullname} за {yyyy_mm}"
    email.to = [
        client.email,
    ]
    email.attach_file(csv_filename)

    try:
        email.send()
        console_log.info(
            f"{remote_ip} -> {query_str} -> отправлено сообщение на {client.email}"
        )
    except BaseException as e:
        return render(
            request,
            "reestr/error.html",
            {"err_str": "ошибка отправки сообщения : " + str(e)},
        )

    try:
        os.remove(csv_filename)
    except BaseException as e:
        return render(
            request,
            "reestr/error.html",
            {"err_str": "файл отправлен, но не удален : " + str(e)},
        )

    return render(
        request,
        "reestr/send_email.html",
        {"send_str": f"отправлено на адрес {client.email}"},
    )
