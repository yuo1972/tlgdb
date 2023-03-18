from datetime import datetime, timezone
from enum import Enum

from .models import TlgTarif, TlgTarifCountry, Country


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


TypeDelivery = Enum("TTarif", "ORDINARY URGENT POSTZ ABOX", start=1)
TypeNotification = Enum(
    "TypeNotification", "NOT_NOTIFICATION ORD_NOTIFICATION URG_NOTIFICATION", start=1
)
TypeLux = Enum("TypeLux", "NOT_LUX ORD_LUX VIS_LUX", start=1)


class TCalc:
    alarm = ""

    def __init__(
        self,
        datetlg,
        t_delivery=TypeDelivery.ORDINARY,
        t_notification=TypeNotification.NOT_NOTIFICATION,
        t_lux=TypeLux.NOT_LUX,
        t_service=False,
        t_todate=False,
        n_word=0,
        country="Россия",
    ):

        self.cost = 0
        self.cost_nds = 0
        self.cost_word = 0
        self.cost_delivery = 0
        self.cost_notification = 0
        self.cost_lux = 0
        self.cost_todate = 0
        self.cost_service = 0

        self.permit_delivery_post = True
        self.permit_delivery_box = True
        self.permit_notification_ordinary = True
        self.permit_notification_urgent = True
        self.permit_lux_ordinary = True
        self.permit_lux_visual = True
        self.permit_todate = True

        if type(datetlg) == datetime:
            self.dt = datetlg
        else:
            try:
                self.dt = utc_to_local(datetime.strptime(datetlg, "%Y-%m-%d"))
            except ValueError:
                self.alarm = "неправильная дата (ожидается в формате ГГГГ-ММ-ДД)"
                return

        self.type_delivery = t_delivery
        self.type_notification = t_notification
        self.type_lux = t_lux
        self.type_service = t_service
        self.type_todate = t_todate

        if n_word < 0:
            self.alarm = "неправильное количество слов : " + str(n_word)
            self.num_word = 0
        else:
            self.num_word = n_word

        self.ttar = TlgTarif.objects.filter(
            date_begin__lte=self.dt, date_end__gt=self.dt
        )
        if not len(self.ttar):
            self.alarm = "тариф (Россия) за указанную дату не найден"
            return

        if country != "Россия":
            country0 = Country.objects.filter(name_country=country)
            if not len(country0):
                self.alarm = "страна не найдена"
                return

            self.ttar_country = TlgTarifCountry.objects.filter(
                date_begin__lte=self.dt,
                date_end__gt=self.dt,
                country__name_country=country,
            )
            if not len(self.ttar_country):
                self.alarm = "тариф (экс-СССР) за указанную дату не найден"
                return

            self.word_ordinary = self.ttar_country[0].word_ordinary
            self.word_urgent = self.ttar_country[0].word_urgent

            self.permit_delivery_post = self.ttar_country[0].country.delivery_post_bool
            self.permit_delivery_box = self.ttar_country[0].country.delivery_box_bool
            self.permit_notification_ordinary = self.ttar_country[
                0
            ].country.notification_ordinary_bool
            self.permit_notification_urgent = self.ttar_country[
                0
            ].country.notification_urgent_bool
            self.permit_lux_ordinary = self.ttar_country[0].country.lux_ordinary_bool
            self.permit_lux_visual = self.ttar_country[0].country.lux_visual_bool
            self.permit_todate = self.ttar_country[0].country.todate_bool

        else:
            self.word_ordinary = self.ttar[0].word_ordinary
            self.word_urgent = self.ttar[0].word_urgent

        self.calculate()

    def set_num_word(self, n_word):
        self.num_word = n_word
        self.calculate()

    def set_type_delivery(self, t_delivery):
        self.type_delivery = t_delivery
        self.calculate()

    def set_type_notification(self, t_notification):
        self.type_notification = t_notification
        self.calculate()

    def set_type_lux(self, t_lux):
        self.type_lux = t_lux
        self.calculate()

    def set_type_service(self, t_service):
        self.type_service = t_service
        self.calculate()

    def set_type_todate(self, t_todate):
        self.type_todate = t_todate
        self.calculate()

    def calculate(self):
        self.cost = 0
        self.cost_nds = 0
        self.cost_word = 0
        self.cost_delivery = 0
        self.cost_notification = 0
        self.cost_lux = 0
        self.cost_todate = 0
        self.cost_service = 0

        if not len(self.ttar):
            self.alarm = "тариф (Россия) за указанную дату не найден"
            return

        if self.type_service:
            self.cost_service = self.ttar[0].service
            self.cost += self.cost_service

        if self.type_todate:
            self.cost_todate = self.ttar[0].todate
            self.cost += self.cost_todate

        if self.type_lux == TypeLux.ORD_LUX:
            self.cost_lux = self.ttar[0].lux_ordinary
            self.cost += self.cost_lux
        elif self.type_lux == TypeLux.VIS_LUX:
            self.cost_lux = self.ttar[0].lux_visual
            self.cost += self.cost_lux

        if self.type_notification == TypeNotification.ORD_NOTIFICATION:
            self.cost_notification = self.ttar[0].notification_ordinary
            self.cost += self.cost_notification
        elif self.type_notification == TypeNotification.URG_NOTIFICATION:
            self.cost_notification = self.ttar[0].notification_urgent
            self.cost += self.cost_notification

        if self.type_delivery == TypeDelivery.ORDINARY:
            self.cost_delivery = self.ttar[0].delivery_ordinary
            self.cost_word = self.word_ordinary * self.num_word
        elif self.type_delivery == TypeDelivery.URGENT:
            self.cost_delivery = self.ttar[0].delivery_urgent
            self.cost_word = self.word_urgent * self.num_word
        elif self.type_delivery == TypeDelivery.POSTZ:
            self.cost_delivery = self.ttar[0].delivery_post
            self.cost_word = self.word_ordinary * self.num_word
        elif self.type_delivery == TypeDelivery.ABOX:
            self.cost_delivery = self.ttar[0].delivery_box
            self.cost_word = self.word_ordinary * self.num_word

        self.cost += self.cost_delivery + self.cost_word

        self.cost_nds = self.cost * (100 + self.ttar[0].nds_percent) / 100

        self.chk_type()
        self.chk_permit_type()

    def chk_type(self):
        if (
            self.type_notification
            in (TypeNotification.ORD_NOTIFICATION, TypeNotification.URG_NOTIFICATION)
            and self.type_delivery == TypeDelivery.POSTZ
        ):
            self.alarm = (
                "несовместимые типы телеграмм: УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ и ПОЧТОЙ ЗАКАЗНОЕ"
            )

        if (
            self.type_notification
            in (TypeNotification.ORD_NOTIFICATION, TypeNotification.URG_NOTIFICATION)
            and self.type_delivery == TypeDelivery.ABOX
        ):
            self.alarm = "несовместимые типы телеграмм: УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ и ДО ВОСТРЕБОВАНИЯ (А/Я)"

        if (
            self.type_notification
            in (TypeNotification.ORD_NOTIFICATION, TypeNotification.URG_NOTIFICATION)
            and self.type_service
        ):
            self.alarm = (
                "несовместимые типы телеграмм: УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ и СЛУЖЕБНАЯ"
            )

        if (
            self.type_notification == TypeNotification.URG_NOTIFICATION
            and self.type_todate
        ):
            self.alarm = (
                "несовместимые типы телеграмм: УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ и ВРУЧИТЬ"
            )

        if self.type_todate and self.type_delivery == TypeDelivery.URGENT:
            self.alarm = "несовместимые типы телеграмм: ВРУЧИТЬ и СРОЧНАЯ"

        if self.type_todate and self.type_delivery == TypeDelivery.POSTZ:
            self.alarm = "несовместимые типы телеграмм: ВРУЧИТЬ и ПОЧТОЙ ЗАКАЗНОЕ"

        if self.type_todate and self.type_delivery == TypeDelivery.ABOX:
            self.alarm = (
                "несовместимые типы телеграмм: ВРУЧИТЬ и ДО ВОСТРЕБОВАНИЯ (А/Я)"
            )

        if self.type_todate and self.type_service:
            self.alarm = "несовместимые типы телеграмм: ВРУЧИТЬ и СЛУЖЕБНАЯ"

        if self.type_service and self.type_delivery == TypeDelivery.POSTZ:
            self.alarm = "несовместимые типы телеграмм: СЛУЖЕБНАЯ и ПОЧТОЙ ЗАКАЗНОЕ"

        if self.type_service and self.type_delivery == TypeDelivery.ABOX:
            self.alarm = (
                "несовместимые типы телеграмм: СЛУЖЕБНАЯ и ДО ВОСТРЕБОВАНИЯ (А/Я)"
            )

        if self.type_lux in (TypeLux.ORD_LUX, TypeLux.VIS_LUX) and self.type_service:
            self.alarm = "несовместимые типы телеграмм: ЛЮКС и СЛУЖЕБНАЯ"

    def chk_permit_type(self):
        if not self.permit_delivery_post and self.type_delivery == TypeDelivery.POSTZ:
            self.alarm = "неразрешенный тип телеграммы: ПОЧТОЙ ЗАКАЗНОЕ"

        if not self.permit_delivery_box and self.type_delivery == TypeDelivery.ABOX:
            self.alarm = "неразрешенный тип телеграммы: ДО ВОСТРЕБОВАНИЯ (А/Я)"

        if (
            not self.permit_notification_ordinary
            and self.type_notification == TypeNotification.ORD_NOTIFICATION
        ):
            self.alarm = "неразрешенный тип телеграммы: УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ"

        if (
            not self.permit_notification_urgent
            and self.type_notification == TypeNotification.URG_NOTIFICATION
        ):
            self.alarm = "неразрешенный тип телеграммы: УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ"

        if not self.permit_lux_ordinary and self.type_lux == TypeLux.ORD_LUX:
            self.alarm = "неразрешенный тип телеграммы: ЛЮКС"

        if not self.permit_lux_visual and self.type_lux == TypeLux.VIS_LUX:
            self.alarm = "неразрешенный тип телеграммы: ЛЮКС/В"

        if not self.permit_todate and self.type_todate:
            self.alarm = "неразрешенный тип телеграммы: ВРУЧИТЬ"
