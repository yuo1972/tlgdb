from django.test import TestCase
from django.db import connection

from .models import TlgTarif, Country, TlgTarifCountry
from .tcalc import TCalc, TypeDelivery, TypeNotification, TypeLux


def run_field_parameter_test(
    model, self_, field_and_parameter_value: dict, parameter_name: str
) -> None:
    """Тестирует значение параметра для всех объектов модели"""

    for instance in model.objects.all():
        # Пример 1: field = "email"; expected_value = 256.
        # Пример 2: field = "email"; expected_value = "Электронная почта".
        for field, expected_value in field_and_parameter_value.items():
            parameter_real_value = getattr(
                instance._meta.get_field(field), parameter_name
            )

            self_.assertEqual(parameter_real_value, expected_value)


class TestMaxLengthMixin:
    """Миксин для проверки max_length"""

    def run_max_length_test(self, model):
        """Метод, тестирующий max_length"""

        run_field_parameter_test(model, self, self.field_and_max_length, "max_length")


class TestVerboseNameMixin:
    """Миксин для проверки verbose_name"""

    def run_verbose_name_test(self, model):
        """Метод, тестирующий verbose_name"""

        run_field_parameter_test(
            model, self, self.field_and_verbose_name, "verbose_name"
        )


class CountryTests(TestCase, TestMaxLengthMixin, TestVerboseNameMixin):
    """тестирование модели Country"""

    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(name_country="Россия")
        cls.name_country = cls.country._meta.get_field("name_country")

        cls.field_and_max_length = {
            "name_country": 15,
        }

        cls.field_and_verbose_name = {
            "delivery_post_bool": "ПОЧТОЙ ЗАКАЗНОЕ",
            "delivery_box_bool": "ДО ВОСТРЕБОВАНИЯ",
            "notification_ordinary_bool": "УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ",
            "notification_urgent_bool": "УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ",
            "lux_ordinary_bool": "ЛЮКС / ДЕЛЮКС",
            "lux_visual_bool": "ЛЮКС/В",
            "todate_bool": "ВРУЧИТЬ",
        }

    def test_verbose_name(self):
        super().run_verbose_name_test(Country)

    def test_max_length(self):
        super().run_max_length_test(Country)

    def test_string_representation(self):
        """Тест строкового отображения"""

        self.assertEqual(str(self.country), str(self.country.name_country))

    def test_model_verbose_name_plural(self):
        self.assertEqual(Country._meta.verbose_name_plural, "Страны экс-СССР")


class TarifTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        with connection.cursor() as cursor:
            query = """
                INSERT INTO `tlgtarif_country` (`id`, `name_country`, `delivery_box_bool`, `delivery_post_bool`, 
                                                `lux_ordinary_bool`, `lux_visual_bool`, `notification_ordinary_bool`, 
                                                `notification_urgent_bool`, `todate_bool`) 
                VALUES
                (1, 'Армения', 0, 1, 1, 0, 0, 0, 1),
                (2, 'Грузия', 0, 0, 0, 0, 0, 0, 0);
            """
            cursor.execute(query)

            query = """
                INSERT INTO `tlgtarif_tlgtarifcountry` (`id`, `date_begin`, `date_end`, `word_ordinary`, 
                                                        `word_urgent`, `country_id`) 
                VALUES
                (1, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:00.000000', 10.0, 20.0, 1),
                (2, '2020-03-31 21:00:00.000000', '2028-11-30 20:59:00.000000', 15.0, 40.0, 2);
            """
            cursor.execute(query)

            query = """
                INSERT INTO `tlgtarif_tlgtarif` (`id`, `date_begin`, `date_end`, `delivery_ordinary`, `delivery_urgent`, 
                                                `delivery_post`, `delivery_box`, `word_ordinary`, `word_urgent`, 
                                                `notification_ordinary`, `notification_urgent`, `lux_ordinary`, 
                                                `lux_visual`, `todate`, `nds_percent`) 
                VALUES
                (1, '2021-12-31 21:00:00.000000', '2028-12-21 20:59:00.000000', 
                        47.5, 64, 64, 47, 5, 7, 165, 220, 21, 63, 25, 20),
                (2, '2020-12-31 21:00:00.000000', '2021-12-31 20:59:59.000000', 
                        43, 59, 59, 43, 4, 5.7, 150, 200, 21, 63, 25, 20);
            """
            cursor.execute(query)

    def test_tcalc(self):
        """ " тестирование логики класса TCalc"""

        tc = TCalc("2022-01-02")  # минимальное число параметров, НДС
        self.assertEqual((tc.cost_nds, tc.alarm), (57, ""))

        tc = TCalc("2029-01-02")  # дата, на которую нет тарифа
        self.assertEqual(tc.alarm, "тариф (Россия) за указанную дату не найден")

        tc = TCalc("20220102")  # неправильный формат даты
        self.assertEqual(tc.alarm, "неправильная дата (ожидается в формате ГГГГ-ММ-ДД)")

        tc = TCalc("2021-01-02", n_word=-1)  # неправильное количество слов
        self.assertNotEqual(tc.alarm, "")

        tc1 = TCalc("2022-01-02")  # проверка дефолтных значений
        tc2 = TCalc(
            "2022-01-02",
            t_delivery=TypeDelivery.ORDINARY,
            t_notification=TypeNotification.NOT_NOTIFICATION,
            t_lux=TypeLux.NOT_LUX,
            t_service=False,
            t_todate=False,
            n_word=0,
            country="Россия",
        )
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc(
            "2021-01-02", n_word=10, country="Россия"
        )  # считаем слова по второму тарифу
        self.assertEqual((tc1.cost, tc1.alarm), (83, ""))
        tc2 = TCalc("2021-01-02")
        tc2.set_num_word(10)  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc(
            "2021-01-02", n_word=10, t_delivery=TypeDelivery.URGENT
        )  # срочная тлг
        self.assertEqual((tc1.cost, tc1.alarm), (116, ""))
        tc2 = TCalc("2021-01-02", n_word=10)
        tc2.set_type_delivery(TypeDelivery.URGENT)  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc(
            "2021-01-02", n_word=10, t_delivery=TypeDelivery.POSTZ
        )  # ПОЧТОЙ ЗАКАЗНОЕ
        self.assertEqual((tc1.cost, tc1.alarm), (99, ""))
        tc2 = TCalc("2021-01-02", n_word=10)
        tc2.set_type_delivery(TypeDelivery.POSTZ)  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc(
            "2021-01-02", n_word=10, t_delivery=TypeDelivery.ABOX
        )  # ДО ВОСТРЕБОВАНИЯ
        self.assertEqual((tc1.cost, tc1.alarm), (83, ""))
        tc2 = TCalc("2021-01-02", n_word=10)
        tc2.set_type_delivery(TypeDelivery.ABOX)  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc(
            "2021-01-02", n_word=10, t_notification=TypeNotification.ORD_NOTIFICATION
        )  # УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ
        self.assertEqual((tc1.cost, tc1.alarm), (233, ""))
        tc2 = TCalc("2021-01-02", n_word=10)
        tc2.set_type_notification(
            TypeNotification.ORD_NOTIFICATION
        )  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc(
            "2021-01-02", n_word=10, t_notification=TypeNotification.URG_NOTIFICATION
        )  # УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ
        self.assertEqual((tc1.cost, tc1.alarm), (283, ""))
        tc2 = TCalc("2021-01-02", n_word=10)
        tc2.set_type_notification(
            TypeNotification.URG_NOTIFICATION
        )  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc("2021-01-02", n_word=10, t_lux=TypeLux.ORD_LUX)  # ЛЮКС
        self.assertEqual((tc1.cost, tc1.alarm), (104, ""))
        tc2 = TCalc("2021-01-02", n_word=10)
        tc2.set_type_lux(TypeLux.ORD_LUX)  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc("2021-01-02", n_word=10, t_lux=TypeLux.VIS_LUX)  # ЛЮКС/В
        self.assertEqual((tc1.cost, tc1.alarm), (146, ""))
        tc2 = TCalc("2021-01-02", n_word=10)
        tc2.set_type_lux(TypeLux.VIS_LUX)  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc("2021-01-02", n_word=10, t_service=True)  # СЛУЖЕБНАЯ
        self.assertEqual((tc1.cost, tc1.alarm), (186, ""))
        tc2 = TCalc("2021-01-02", n_word=10)
        tc2.set_type_service(True)  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc("2021-01-02", n_word=10, t_todate=True)  # ВРУЧИТЬ
        self.assertEqual((tc1.cost, tc1.alarm), (108, ""))
        tc2 = TCalc("2021-01-02", n_word=10)
        tc2.set_type_todate(True)  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc(
            "2021-01-02",
            n_word=10,
            t_notification=TypeNotification.ORD_NOTIFICATION,
            t_lux=TypeLux.ORD_LUX,
        )  # комбинация УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ + ЛЮКС
        self.assertEqual((tc1.cost, tc1.alarm), (254, ""))
        tc2 = TCalc("2021-01-02", n_word=10)
        tc2.set_type_notification(
            TypeNotification.ORD_NOTIFICATION
        )  # тоже самое через отдельную функцию
        tc2.set_type_lux(TypeLux.ORD_LUX)
        self.assertEqual(tc1.cost, tc2.cost)
        #                                -------------------   несовместимые типы телеграмм
        tc = TCalc(
            "2021-01-02",
            t_notification=TypeNotification.ORD_NOTIFICATION,
            t_delivery=TypeDelivery.POSTZ,
        )  # УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ и ПОЧТОЙ ЗАКАЗНОЕ
        self.assertNotEqual(tc.alarm, "")
        tc = TCalc(
            "2021-01-02",
            t_notification=TypeNotification.URG_NOTIFICATION,
            t_delivery=TypeDelivery.POSTZ,
        )  # УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ и ПОЧТОЙ ЗАКАЗНОЕ
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc(
            "2021-01-02",
            t_notification=TypeNotification.ORD_NOTIFICATION,
            t_delivery=TypeDelivery.ABOX,
        )  # УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ и ДО ВОСТРЕБОВАНИЯ
        self.assertNotEqual(tc.alarm, "")
        tc = TCalc(
            "2021-01-02",
            t_notification=TypeNotification.URG_NOTIFICATION,
            t_delivery=TypeDelivery.ABOX,
        )  # УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ и ДО ВОСТРЕБОВАНИЯ
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc(
            "2021-01-02",
            t_notification=TypeNotification.ORD_NOTIFICATION,
            t_service=True,
        )  # УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ и СЛУЖЕБНАЯ
        self.assertNotEqual(tc.alarm, "")
        tc = TCalc(
            "2021-01-02",
            t_notification=TypeNotification.URG_NOTIFICATION,
            t_service=True,
        )  # УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ и СЛУЖЕБНАЯ
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc(
            "2021-01-02",
            t_notification=TypeNotification.URG_NOTIFICATION,
            t_todate=True,
        )  # УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ и ВРУЧИТЬ
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc(
            "2021-01-02", t_delivery=TypeDelivery.URGENT, t_todate=True
        )  # СРОЧНАЯ и ВРУЧИТЬ
        self.assertNotEqual(tc.alarm, "")
        tc = TCalc(
            "2021-01-02", t_delivery=TypeDelivery.POSTZ, t_todate=True
        )  # ПОЧТОЙ ЗАКАЗНОЕ и ВРУЧИТЬ
        self.assertNotEqual(tc.alarm, "")
        tc = TCalc(
            "2021-01-02", t_delivery=TypeDelivery.ABOX, t_todate=True
        )  # ДО ВОСТРЕБОВАНИЯ и ВРУЧИТЬ
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc("2021-01-02", t_service=True, t_todate=True)  # СЛУЖЕБНАЯ и ВРУЧИТЬ
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc(
            "2021-01-02", t_service=True, t_delivery=TypeDelivery.POSTZ
        )  # СЛУЖЕБНАЯ и ПОЧТОЙ ЗАКАЗНОЕ
        self.assertNotEqual(tc.alarm, "")
        tc = TCalc(
            "2021-01-02", t_service=True, t_delivery=TypeDelivery.ABOX
        )  # СЛУЖЕБНАЯ и ДО ВОСТРЕБОВАНИЯ
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc(
            "2021-01-02", t_service=True, t_lux=TypeLux.ORD_LUX
        )  # СЛУЖЕБНАЯ и ЛЮКС
        self.assertNotEqual(tc.alarm, "")
        tc = TCalc(
            "2021-01-02", t_service=True, t_lux=TypeLux.VIS_LUX
        )  # СЛУЖЕБНАЯ и ЛЮКС/В
        self.assertNotEqual(tc.alarm, "")
        #                                ---------------- экс-СССР
        tc = TCalc("2022-01-02", country="Армения")  # минимальное число параметров, НДС
        self.assertEqual((tc.cost_nds, tc.alarm), (57, ""))

        tc = TCalc("2028-12-02", country="Армения")  # дата, на которую нет тарифа
        self.assertEqual(tc.alarm, "тариф (экс-СССР) за указанную дату не найден")

        tc = TCalc("2022-01-02", country="Бразилия")  # страны нет в базе
        self.assertEqual(tc.alarm, "страна не найдена")

        tc1 = TCalc(
            "2022-01-02", n_word=10, country="Армения"
        )  # разные страны с разными тарифами
        tc2 = TCalc("2022-01-02", n_word=10, country="Грузия")
        self.assertNotEqual(tc1.cost, tc2.cost)

        tc1 = TCalc("2021-01-02", n_word=10, country="Армения")  # обычная тлг
        self.assertEqual((tc1.cost, tc1.alarm), (143, ""))
        tc2 = TCalc("2021-01-02", country="Армения")
        tc2.set_num_word(10)  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc(
            "2021-01-02", n_word=10, t_delivery=TypeDelivery.URGENT, country="Армения"
        )  # срочная тлг
        self.assertEqual((tc1.cost, tc1.alarm), (259, ""))
        tc2 = TCalc("2021-01-02", n_word=10, country="Армения")
        tc2.set_type_delivery(TypeDelivery.URGENT)  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)

        tc1 = TCalc(
            "2021-01-02", n_word=10, t_lux=TypeLux.ORD_LUX, country="Армения"
        )  # ЛЮКС
        self.assertEqual((tc1.cost, tc1.alarm), (164, ""))
        tc2 = TCalc("2021-01-02", n_word=10, country="Армения")
        tc2.set_type_lux(TypeLux.ORD_LUX)  # тоже самое через отдельную функцию
        self.assertEqual(tc1.cost, tc2.cost)
        #                                 -------------- неразрешенные типы телеграмм
        tc = TCalc(
            "2021-01-02", t_delivery=TypeDelivery.POSTZ, country="Грузия"
        )  # ПОЧТОЙ ЗАКАЗНОЕ
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc(
            "2021-01-02", t_delivery=TypeDelivery.ABOX, country="Грузия"
        )  # ДО ВОСТРЕБОВАНИЯ
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc(
            "2021-01-02",
            t_notification=TypeNotification.ORD_NOTIFICATION,
            country="Грузия",
        )  # УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc(
            "2021-01-02",
            t_notification=TypeNotification.URG_NOTIFICATION,
            country="Грузия",
        )  # УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc("2021-01-02", t_lux=TypeLux.ORD_LUX, country="Грузия")  # ЛЮКС
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc("2021-01-02", t_lux=TypeLux.VIS_LUX, country="Грузия")  # ЛЮКС/В
        self.assertNotEqual(tc.alarm, "")

        tc = TCalc("2021-01-02", t_todate=True, country="Грузия")  # ВРУЧИТЬ
        self.assertNotEqual(tc.alarm, "")


class TarifTestCase(TestCase):
    fixtures = [
        "tlgtarif.json",
    ]

    def test_calculator_html(self):
        response = self.client.get("/tlgtarif/calculator/")
        self.assertEqual(response.status_code, 200)

    def test_import_negative(self):
        response = self.client.get("/tlgtarif/import/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "<title>Error</title>"
        )  # проверяет сообщение об ошибке (поскольку данные уже загружены из фикстур)

    def test_tlist_html(self):
        response = self.client.get("/tlgtarif/tlist/", {"date": "2022-01-01"})
        self.assertEqual(response.status_code, 200)

        response2 = self.client.get("/tlgtarif/tlist/")  # параметр date не указан
        self.assertEqual(response2.status_code, 200)

    def test_tlist_html_negative(self):
        response = self.client.get("/tlgtarif/tlist/", {"date": "2000-01-01"})
        self.assertContains(
            response, "<title>Error</title>"
        )  # нет тарифа за указанную дату

        response = self.client.get("/tlgtarif/tlist/", {"date": "asddfg"})
        self.assertContains(response, "<title>Error</title>")  # искаженная дата

    def test_tcalc_api(self):
        response = self.client.get(
            "/tlgtarif/tcalc/api/", {"country": "Россия", "date": "2022-01-01"}
        )
        self.assertEqual(
            response.json()["cost_summ"], "43.00"
        )  # минимальное число параметров

        response2 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {"country": "Россия", "date": "2022-01-01", "numword": 10},
        )
        response02 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {
                "country": "Россия",
                "date": "2022-01-01",
                "numword": 10,
                "radioord": "true",
            },
        )
        self.assertEqual(response2.json()["cost_summ"], "83.00")
        self.assertEqual(
            response2.json()["cost_summ"], response02.json()["cost_summ"]
        )  # default radioord=true

        response3 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {"country": "Россия", "date": "2022-01-01", "numword": 10, "lux": "true"},
        )
        self.assertEqual(response3.json()["cost_summ"], "104.00")

        response4 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {"country": "Россия", "date": "2022-01-01", "numword": 10, "luxv": "true"},
        )
        self.assertEqual(response4.json()["cost_summ"], "146.00")

        response5 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {"country": "Россия", "date": "2022-01-01", "numword": 10, "notif": "true"},
        )
        self.assertEqual(response5.json()["cost_summ"], "233.00")

        response6 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {
                "country": "Россия",
                "date": "2022-01-01",
                "numword": 10,
                "notifurg": "true",
            },
        )
        self.assertEqual(response6.json()["cost_summ"], "283.00")

        response7 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {
                "country": "Россия",
                "date": "2022-01-01",
                "numword": 10,
                "service": "true",
            },
        )
        self.assertEqual(response7.json()["cost_summ"], "186.00")

        response8 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {
                "country": "Россия",
                "date": "2022-01-01",
                "numword": 10,
                "todate": "true",
            },
        )
        self.assertEqual(response8.json()["cost_summ"], "108.00")

        response9 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {
                "country": "Россия",
                "date": "2022-01-01",
                "numword": 10,
                "radiourg": "true",
            },
        )
        self.assertEqual(response9.json()["cost_summ"], "116.00")

        response10 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {
                "country": "Россия",
                "date": "2022-01-01",
                "numword": 10,
                "radiopost": "true",
            },
        )
        self.assertEqual(response10.json()["cost_summ"], "99.00")

        response11 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {
                "country": "Россия",
                "date": "2022-01-01",
                "numword": 10,
                "radiobox": "true",
            },
        )
        self.assertEqual(response11.json()["cost_summ"], "83.00")

    def test_tcalc_api_negativ(self):
        response = self.client.get(
            "/tlgtarif/tcalc/api/", {"country": "123", "date": "2022-01-01"}
        )
        self.assertEqual(response.json()["errorAlert"], "страна не найдена")

        response2 = self.client.get(
            "/tlgtarif/tcalc/api/", {"country": "Россия", "date": "2022-01-пп"}
        )
        self.assertEqual(
            response2.json()["errorAlert"],
            "неправильная дата (ожидается в формате ГГГГ-ММ-ДД)",
        )

        response3 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {"country": "Россия", "date": "2022-01-01", "numword": 10, "lux": "true1"},
        )
        self.assertEqual(
            response3.json()["errorAlert"],
            "неправильное значение параметра 'lux' : true1",
        )

        response4 = self.client.get(
            "/tlgtarif/tcalc/api/",  # некорректное количество слов
            {"country": "Россия", "date": "2022-01-01", "numword": -1},
        )
        self.assertNotEqual(response4.json()["errorAlert"], "")

        response5 = self.client.get(
            "/tlgtarif/tcalc/api/",  # некорректное количество слов
            {"country": "Россия", "date": "2022-01-01", "numword": "rr"},
        )
        self.assertNotEqual(response5.json()["errorAlert"], "")

        response6 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {
                "country": "Россия",
                "date": "2022-01-01",
                "notifurg": "true",
                "notif": "true",
            },
        )
        self.assertEqual(
            response6.json()["errorAlert"],
            "нельзя выбирать одновременно notif и notifurg",
        )

        response7 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {"country": "Россия", "date": "2022-01-01", "lux": "true", "luxv": "true"},
        )
        self.assertEqual(
            response7.json()["errorAlert"], "нельзя выбирать одновременно lux и luxv"
        )

        response8 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {
                "country": "Россия",
                "date": "2022-01-01",
                "radioord": "true",
                "radiourg": "true",
            },
        )
        self.assertEqual(
            response8.json()["errorAlert"],
            "нельзя выбирать одновременно radioord, radiobox, radiopost и radiourg",
        )

        response9 = self.client.get(
            "/tlgtarif/tcalc/api/",
            {"country": "Россия", "date": "2022-01-01", "radioord": "false"},
        )
        self.assertEqual(
            response9.json()["errorAlert"],
            "должен быть выбран хотя бы один из radioord, radiobox, radiopost и radiourg",
        )

        response10 = self.client.get(
            "/tlgtarif/tcalc/api/",  # несовместимые типы телеграмм
            {
                "country": "Россия",
                "date": "2022-01-01",
                "service": "true",
                "todate": "true",
            },
        )
        self.assertNotEqual(response10.json()["errorAlert"], "")
