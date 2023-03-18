from django.test import TestCase

from .models import TypeNotiifcationR, TypeLuxR, TypeUrgentR

from .util import (
    get_type_lux,
    get_type_notification,
    get_type_urgent,
    get_num_word,
    is_todate,
)


class UtilTests(TestCase):
    def test_lux(self):
        response = get_type_lux("СРОЧНАЯ люкс РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeLuxR.ORD_LUX)

        response = get_type_lux("СРОЧНАЯ ДЕЛЮКС РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeLuxR.ORD_LUX)

        response = get_type_lux("ЛЮКС/В РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeLuxR.VIS_LUX)

        response = get_type_lux("ЛЮКС/И РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeLuxR.VIS_LUX)

    def test_lux_negative(self):
        response = get_type_lux("СРОЧНАЯ люс РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeLuxR.NOT_LUX)

    def test_notif(self):
        response = get_type_notification("УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeNotiifcationR.ORD_NOTIFICATION)

        response = get_type_notification(
            "УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ РОСТОВ-НА-ДОНУ ...", 1
        )
        self.assertEqual(response, TypeNotiifcationR.URG_NOTIFICATION)

        response = get_type_notification("РОСТОВ-НА-ДОНУ ...", 1)
        self.assertEqual(response, TypeNotiifcationR.ORD_NOTIFICATION)

        response = get_type_notification(
            "УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ РОСТОВ-НА-ДОНУ ..."
        )
        self.assertEqual(response, TypeNotiifcationR.URG_NOTIFICATION)

        response = get_type_notification(
            "СРОЧНОЕ увеДОМЛЕНИЕ ТЕЛЕГРАФОМ РОСТОВ-НА-ДОНУ ..."
        )
        self.assertEqual(response, TypeNotiifcationR.ORD_NOTIFICATION)

    def test_notif_negative(self):
        response = get_type_notification("УВЕДОМЛЕНИЕ ТЕЛЕГРАФО РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeNotiifcationR.NOT_NOTIFICATION)

    def test_urgent(self):
        response = get_type_urgent("СРОЧНАЯ РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeUrgentR.URGENT)

        response = get_type_urgent("сроЧНАЯ РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeUrgentR.URGENT)

        response = get_type_urgent("ПРАВИТЕЛЬСТВЕННАЯ РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeUrgentR.URGENT)

        response = get_type_urgent("РОСТОВ-НА-ДОНУ ...", 1)
        self.assertEqual(response, TypeUrgentR.URGENT)

        response = get_type_urgent("РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeUrgentR.ORDINARY)

        response = get_type_urgent("ПОЧТОЙ ЗАКАЗНОЕ РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeUrgentR.POSTZ)

        response = get_type_urgent("А/Я РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeUrgentR.ABOX)

        response = get_type_urgent("ДО ВОСТРЕБОВАНИЯ РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeUrgentR.ABOX)

        response = get_type_urgent("ДО    ВОСТРЕБОВАНИЯ РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeUrgentR.ABOX)

    def test_urgent_negative(self):
        response = get_type_urgent("ПОЧТОЙЗАКАЗНОЕ РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeUrgentR.ORDINARY)

        response = get_type_urgent("ПРАВИТЕЛЬСТВЕННА РОСТОВ-НА-ДОНУ ...")
        self.assertEqual(response, TypeUrgentR.ORDINARY)

    def test_num_word(self):
        response = get_num_word("РОСТОВ-НА-ДОНУ 2/8010 19 01/08 1615")
        self.assertEqual(int(response), 19)

        response = get_num_word("ТАГАНРОГ РОСТОВСКОЙ 655/5 21 01/08 1625")
        self.assertEqual(int(response), 21)

        response = get_num_word("МОСКВА 324113 30 01/08 1912 ")
        self.assertEqual(int(response), 30)

        response = get_num_word("МОСКВА 324113 Б/С 01/08 1912 ")
        self.assertEqual(int(response), 0)

    def test_num_word_negative(self):
        response = get_num_word("РОСТОВ-НА-ДОНУ 2/8010 01/08 1615")
        self.assertEqual(int(response), 0)

        response = get_num_word("ТАГАНРОГ РОСТОВСКОЙ 21 01/08 1625")
        self.assertEqual(int(response), 0)

    def test_todate(self):
        response = is_todate("РОСТОВ-НА-ДОНУ ... ВРУЧИТЬ 20/02")
        self.assertEqual(response, True)

        response = is_todate("РОСТОВ-НА-ДОНУ ... ВРУЧить 20.02")
        self.assertEqual(response, True)

    def test_todate_negative(self):
        response = is_todate("РОСТОВ-НА-ДОНУ ... ВРУЧИТ 20/02")
        self.assertEqual(response, False)
