from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError

from .models import TlgTarif, Country, TlgTarifCountry


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    change_list_template = "admin/tar_change_list.html"

    # list_display = (
    #     "un_name",
    #     "inp_gate_date",
    # )
    # readonly_fields = ["timestamp_start", "timestamp_end"]
    # list_filter = ["is_done"]
    # search_fields = ("name",)


# @admin.register(TlgTarif)
# class TlgTarifAdmin(admin.ModelAdmin):
#     change_list_template = "admin/tar_change_list.html"
#
#     list_display = (
#         "__str__",
#         "date_begin",
#         "date_end",
#     )


class TlgTarifForm(forms.ModelForm):
    class Meta:
        model = TlgTarif
        fields = [
            "date_begin",
            "date_end",
            "delivery_ordinary",
            "delivery_urgent",
            "delivery_post",
            "delivery_box",
            "word_ordinary",
            "word_urgent",
            "notification_ordinary",
            "notification_urgent",
            "lux_ordinary",
            "lux_visual",
            "todate",
            "nds_percent",
        ]

    def clean(self):
        cleaned_data = super(TlgTarifForm, self).clean()
        date1 = cleaned_data.get("date_begin")
        date2 = cleaned_data.get("date_end")

        if date1 >= date2:
            raise ValidationError(
                "дата окончания должна быть больше даты начала действия тарифа"
            )

        ttar1 = TlgTarif.objects.filter(
            date_begin__lte=date1, date_end__gt=date1
        ).exclude(id=self.instance.id)
        ttar2 = TlgTarif.objects.filter(
            date_begin__gte=date1, date_begin__lt=date2
        ).exclude(id=self.instance.id)
        if len(ttar1) or len(ttar2):
            raise ValidationError(
                "интервал действия тарифа пересекается с уже существующим"
            )

        return cleaned_data


@admin.register(TlgTarif)
class TlgTarifAdmin(admin.ModelAdmin):
    form = TlgTarifForm

    change_list_template = "admin/tar_change_list.html"

    list_display = (
        "__str__",
        "date_begin",
        "date_end",
    )


# @admin.register(TlgTarifCountry)
# class TlgTarifCountryAdmin(admin.ModelAdmin):
#     change_list_template = "admin/tar_change_list.html"
#
#     list_display = (
#         "__str__",
#         "country",
#         "date_begin",
#         "date_end",
#     )


class TlgTarifCountryForm(forms.ModelForm):
    class Meta:
        model = TlgTarifCountry
        fields = [
            "country",
            "date_begin",
            "date_end",
            "word_ordinary",
            "word_urgent",
        ]

    def clean(self):
        cleaned_data = super(TlgTarifCountryForm, self).clean()
        date1 = cleaned_data.get("date_begin")
        date2 = cleaned_data.get("date_end")
        cntr = cleaned_data.get("country")

        if date1 >= date2:
            raise ValidationError(
                "дата окончания должна быть больше даты начала действия тарифа"
            )

        ttar1 = TlgTarifCountry.objects.filter(
            country__name_country=cntr, date_begin__lte=date1, date_end__gt=date1
        ).exclude(id=self.instance.id)
        ttar2 = TlgTarifCountry.objects.filter(
            country__name_country=cntr, date_begin__gte=date1, date_begin__lt=date2
        ).exclude(id=self.instance.id)
        if len(ttar1) or len(ttar2):
            raise ValidationError(
                "интервал действия тарифа пересекается с уже существующим"
            )

        return cleaned_data


@admin.register(TlgTarifCountry)
class TlgTarifCountryAdmin(admin.ModelAdmin):
    form = TlgTarifCountryForm

    change_list_template = "admin/tar_change_list.html"

    list_display = (
        "__str__",
        "country",
        "date_begin",
        "date_end",
    )
