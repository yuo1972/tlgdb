from django.db import models


class TlgTarif(models.Model):
    date_begin = models.DateTimeField(verbose_name="начало действия")
    date_end = models.DateTimeField(verbose_name="окончание действия")
    delivery_ordinary = models.FloatField(default=0, verbose_name="простая")
    delivery_urgent = models.FloatField(default=0, verbose_name="СРОЧНАЯ")
    delivery_post = models.FloatField(default=0, verbose_name="ПОЧТОЙ ЗАКАЗНОЕ")
    delivery_box = models.FloatField(default=0, verbose_name="ДО ВОСТРЕБОВАНИЯ")
    word_ordinary = models.FloatField(default=0, verbose_name="простая")
    word_urgent = models.FloatField(default=0, verbose_name="СРОЧНАЯ")
    notification_ordinary = models.FloatField(
        default=0, verbose_name="УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ"
    )
    notification_urgent = models.FloatField(
        default=0, verbose_name="УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ"
    )
    lux_ordinary = models.FloatField(default=0, verbose_name="ЛЮКС / ДЕЛЮКС")
    lux_visual = models.FloatField(default=0, verbose_name="ЛЮКС/В")
    todate = models.FloatField(default=0, verbose_name="ВРУЧИТЬ")
    nds_percent = models.FloatField(default=0, verbose_name="НДС")

    @property
    def service(
        self,
    ):  # платный служебный запрос - стоимость ответной телеграммы (доставка + 15 слов)
        return self.delivery_ordinary + self.word_ordinary * 15

    def __str__(self):
        return "тариф %d" % self.id

    class Meta:
        verbose_name_plural = "Тарифы, Россия"


class Country(models.Model):
    name_country = models.CharField(max_length=15)
    delivery_post_bool = models.BooleanField(
        default=True, verbose_name="ПОЧТОЙ ЗАКАЗНОЕ"
    )
    delivery_box_bool = models.BooleanField(
        default=False, verbose_name="ДО ВОСТРЕБОВАНИЯ"
    )
    notification_ordinary_bool = models.BooleanField(
        default=False, verbose_name="УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ"
    )
    notification_urgent_bool = models.BooleanField(
        default=False, verbose_name="УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ"
    )
    lux_ordinary_bool = models.BooleanField(default=True, verbose_name="ЛЮКС / ДЕЛЮКС")
    lux_visual_bool = models.BooleanField(default=False, verbose_name="ЛЮКС/В")
    todate_bool = models.BooleanField(default=True, verbose_name="ВРУЧИТЬ")

    def __str__(self):
        return self.name_country

    class Meta:
        verbose_name_plural = "Страны экс-СССР"


class TlgTarifCountry(models.Model):
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, verbose_name="страна"
    )
    date_begin = models.DateTimeField(verbose_name="начало действия")
    date_end = models.DateTimeField(verbose_name="окончание действия")
    word_ordinary = models.FloatField(default=0, verbose_name="простая")
    word_urgent = models.FloatField(default=0, verbose_name="срочная")

    def __str__(self):
        return "тариф %d" % self.id

    class Meta:
        verbose_name_plural = "Тарифы, экс-СССР"
