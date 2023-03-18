import re

from .models import TypeNotiifcationR, TypeLuxR, TypeUrgentR

from datetime import timezone


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def get_type_lux(str):
    if re.search(r"ЛЮКС/[ВИ]", str, flags=re.IGNORECASE):
        return TypeLuxR.VIS_LUX
    elif re.search(r"ЛЮКС", str, flags=re.IGNORECASE):
        return TypeLuxR.ORD_LUX

    return TypeLuxR.NOT_LUX


def get_type_notification(str, flag=0):
    if re.search(r"УВЕДОМЛЕНИЕ\s+ТЕЛЕГРАФОМ\s+СРОЧНОЕ", str, flags=re.IGNORECASE):
        return TypeNotiifcationR.URG_NOTIFICATION
    elif flag or re.search(r"УВЕДОМЛЕНИЕ\s+ТЕЛЕГРАФОМ", str, flags=re.IGNORECASE):
        return TypeNotiifcationR.ORD_NOTIFICATION

    return TypeNotiifcationR.NOT_NOTIFICATION


def get_type_urgent(stru, flag=0):
    if flag or re.search(r"(СРОЧНАЯ)|(ПРАВИТЕЛЬСТВЕННАЯ)", stru, flags=re.IGNORECASE):
        return TypeUrgentR.URGENT
    elif re.search(r"ПОЧТОЙ\s+ЗАКАЗНОЕ", stru, flags=re.IGNORECASE):
        return TypeUrgentR.POSTZ
    elif re.search(r"(ДО\s+ВОСТРЕБОВАНИЯ)|(А/Я)", stru, flags=re.IGNORECASE):
        return TypeUrgentR.ABOX

    return TypeUrgentR.ORDINARY


def get_num_word(ppstr):
    match = re.search("\d/?\d+\s+(\d+)\s+\d", ppstr)
    if match:
        return match[1]
    else:
        return 0


def is_todate(str):
    return True if re.search("ВРУЧИТЬ", str, flags=re.IGNORECASE) else False


def month_rus(mon):
    strmon = [
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря",
    ]
    return strmon[mon - 1]


def float_comma(floatstr):
    return float(floatstr.replace(",", "."))


def get_value_by_name(name, enum):
    for nm, vl in enum.choices:
        if nm == name:
            return vl

    return ""
