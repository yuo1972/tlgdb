from django.test import TestCase

from .views import import0


class TlgTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        import0()  # импортирует 50 тестовых записей в БД

    def test_list(self):
        response = self.client.get("/tlg/list/")
        self.assertContains(
            response, "<TR", count=50
        )  # проверяет наличие 50 строк в таблице

    def test_api_list(self):
        response = self.client.get("/tlg/api/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 50)

    def test_api_filter_date(self):
        response = self.client.get("/tlg/api/", {"datei_before": "2022-08-01"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 7)

    def test_api_filter_chanel(self):
        response = self.client.get(
            "/tlg/api/", {"inp_chan": "123002/03", "out_chan": "123058"}
        )
        self.assertEqual(response.data["count"], 5)

    def test_api_filter_subscribe_ordering_kn(self):
        response = self.client.get(
            "/tlg/api/", {"subscribe": "тамож", "ordering": "-kn"}
        )
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"][0]["un_name"], "op0441f92.q")

    def test_api_filter_un_name(self):
        response = self.client.get("/tlg/api/", {"un_name": "op0441f92.q"})
        self.assertEqual(response.data["count"], 1)

    def test_api_filter_un_name_negative(self):
        response = self.client.get("/tlg/api/", {"un_name": "op0441f92.qqq"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_api_filter_inp_num(self):
        response = self.client.get("/tlg/api/", {"inp_num": "40"})
        self.assertEqual(response.data["count"], 2)

    def test_api_filter_out_num(self):
        response = self.client.get("/tlg/api/", {"out_num": "7"})
        self.assertEqual(response.data["count"], 2)

    def test_api_filter_kn(self):
        response = self.client.get("/tlg/api/", {"kn": "^2/.*05$"})
        self.assertEqual(response.data["count"], 3)

    def test_api_filter_pp_address(self):
        response = self.client.get(
            "/tlg/api/", {"pp": "москва", "address": "ростов на дону"}
        )
        self.assertEqual(response.data["count"], 6)

    def test_api_post_patch_delete(self):
        response = self.client.post(
            "/tlg/api/",
            {
                "un_name": "string1",
                "inp_gate_date": "2023-02-18T07:21:08.140Z",
                "inp_chan": "string",
                "inp_num": "stri",
                "inp_prz": "string",
                "ref": "string",
                "kn": "string",
                "categ": "str",
                "fl_uved_bool": True,
                "fl_urgent_bool": True,
                "pp": "string",
                "address": "string",
                "subscribe": "string",
                "out_gate_date": "2023-02-18T07:21:08.140Z",
                "out_chan": "string",
                "out_num": "stri",
                "out_prz": "string",
            },
        )
        new_id = response.data["id"]
        self.assertEqual(response.data["un_name"], "string1")

        response2 = self.client.patch(
            "/tlg/api/{}/".format(new_id),
            data={"inp_chan": "string2", "inp_num": "123"},
            content_type="application/json",
        )
        self.assertEqual(response2.data["inp_chan"], "string2")

        response3 = self.client.delete("/tlg/api/{}/".format(new_id))
        self.assertEqual(response3.status_code, 204)

        response4 = self.client.get("/tlg/api/")
        self.assertEqual(response4.data["count"], 50)

    def test_api_delete_negative(self):
        response = self.client.delete("/tlg/api/1000/")
        self.assertEqual(response.status_code, 404)

    def test_api_patch_negative(self):
        response = self.client.patch(
            "/tlg/api/1000/",
            data={"inp_chan": "string2", "inp_num": "123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
