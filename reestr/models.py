from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

# from django.db.models.signals import post_save
# from django.dispatch import receiver

from tlg.models import Tlg
from tlgtarif.models import Country


class UserTlg(models.Model):
    """Операторы связи/биллинга"""

    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    index_prefix = models.TextField(
        max_length=12, blank=True, verbose_name="префикс тлг-индекса"
    )
    reestr_bool = models.BooleanField(
        default=True, verbose_name="доступ к формированию реестра"
    )
    billing_bool = models.BooleanField(default=False, verbose_name="доступ к биллингу")
    fullname = models.CharField(max_length=30, blank=True, verbose_name="полное имя")

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name_plural = "Операторы связи/биллинга"


# @receiver(post_save, sender=User)
# def create_user_tlg(sender, instance, created, **kwargs):
#     if created:
#         UserTlg.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_tlg(sender, instance, **kwargs):
#     instance.usertlg.save()


class Client(models.Model):
    """Клиенты, по которым формируются реестры"""

    code = models.CharField(max_length=24, verbose_name="код клиента", unique=True)
    shortname = models.CharField(
        max_length=24, verbose_name="короткое имя", unique=True
    )
    fullname = models.CharField(max_length=50, verbose_name="полное имя", unique=True)
    email = models.EmailField(default=None, verbose_name="электронная почта")

    class Meta:
        verbose_name_plural = "Клиенты"


class Reestr(models.Model):
    """Реестр платных телеграмм"""

    usertlg = models.ForeignKey(
        UserTlg, on_delete=models.CASCADE, related_name="reestrs"
    )
    date = models.DateField(verbose_name="дата реестра")
    date_created = models.DateField(verbose_name="дата формирования реестра")
    fl_created = models.BooleanField(
        default=False, verbose_name="реестр сформирован"
    )  # если 1 - реестр сформирован, можно выставлять счет
    fl_processed = models.BooleanField(
        default=False, verbose_name="счет выставлен"
    )  # если 0 - счет не выставлен, можно исправлять, если 1 - счет выставлен, исправлять нельзя
    signature = models.CharField(
        max_length=20, default="", verbose_name="фамилия оператора"
    )

    class Meta:
        verbose_name_plural = "Реестры"


class TypeUrgentR(models.TextChoices):
    """селектор выбора телеграмм по типу доставки"""

    ORDINARY = "O", _("простая")
    URGENT = "U", _("срочная")
    POSTZ = "P", _("почтой заказная")
    ABOX = "B", _("до востребования")


class TypeNotiifcationR(models.TextChoices):
    """селектор выбора типа телеграмм с уведомлением"""

    NOT_NOTIFICATION = "NN", _("---")
    ORD_NOTIFICATION = "ON", _("уведомление телеграфом")
    URG_NOTIFICATION = "UN", _("уведомление телеграфом срочное")


class TypeLuxR(models.TextChoices):
    """селектор выбора типа телеграмм люкс"""

    NOT_LUX = "NL", _("---")
    ORD_LUX = "LX", _("люкс/делюкс")
    VIS_LUX = "LV", _("люкс/в")


class Record(models.Model):
    """Протарифицированные телеграммы"""

    tlg = models.ForeignKey(Tlg, on_delete=models.CASCADE, related_name="tlg_records")
    autocost_bool = models.BooleanField(default=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="country_records",
    )
    typeUrg = models.CharField(
        max_length=1, choices=TypeUrgentR.choices, default=TypeUrgentR.ORDINARY
    )
    typeNot = models.CharField(
        max_length=2,
        choices=TypeNotiifcationR.choices,
        default=TypeNotiifcationR.NOT_NOTIFICATION,
    )
    typeLX = models.CharField(
        max_length=2, choices=TypeLuxR.choices, default=TypeLuxR.NOT_LUX
    )
    todate_bool = models.BooleanField(
        default=False, verbose_name="Вручить в срок (флаг)"
    )
    kkv_bool = models.BooleanField(default=False, verbose_name="Платный запрос (флаг)")
    num_word = models.IntegerField(default=0, verbose_name="Количество слов")
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="client_records",
    )
    cost_service = models.FloatField(default=0, verbose_name="Платный запрос")
    cost_todate = models.FloatField(
        default=0, verbose_name="Доставка телеграммы в срок, указанный отправителем"
    )
    cost_lux = models.FloatField(default=0, verbose_name="Художественный бланк")
    cost_notif = models.FloatField(default=0, verbose_name="Уведомление о вручении")
    cost_deliv = models.FloatField(default=0, verbose_name="Доставка телеграммы")
    cost_word = models.FloatField(
        default=0, verbose_name="Передача телеграммы, за слово"
    )
    cost = models.FloatField(default=0, verbose_name="Стоимость телеграммы")
    cost_nds = models.FloatField(default=0, verbose_name="Стоимость телеграммы с НДС")
    reestr = models.ForeignKey(
        Reestr, on_delete=models.CASCADE, related_name="reestr_records"
    )

    @property
    def cost_set(self):
        return {
            "country_name": self.country.name_country if self.country else "Россия",
            "typeUrg": self.typeUrg,
            "typeNot": self.typeNot,
            "typeLX": self.typeLX,
            "todate_bool": self.todate_bool,
            "kkv_bool": self.kkv_bool,
            "num_word": self.num_word,
            "cost_service": self.cost_service,
            "cost_todate": self.cost_todate,
            "cost_lux": self.cost_lux,
            "cost_notif": self.cost_notif,
            "cost_deliv": self.cost_deliv,
            "cost_word": self.cost_word,
            "cost": self.cost,
            "cost_nds": self.cost_nds,
        }

    class Meta:
        verbose_name_plural = "Протарифицированные телеграммы"
