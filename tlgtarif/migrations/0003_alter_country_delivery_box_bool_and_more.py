# Generated by Django 4.1.5 on 2023-02-08 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "tlgtarif",
            "0002_country_delivery_box_bool_country_delivery_post_bool_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="country",
            name="delivery_box_bool",
            field=models.BooleanField(default=False, verbose_name="ДО ВОСТРЕБОВАНИЯ"),
        ),
        migrations.AlterField(
            model_name="country",
            name="delivery_post_bool",
            field=models.BooleanField(default=True, verbose_name="ПОЧТОЙ ЗАКАЗНОЕ"),
        ),
        migrations.AlterField(
            model_name="country",
            name="lux_ordinary_bool",
            field=models.BooleanField(default=True, verbose_name="ЛЮКС / ДЕЛЮКС"),
        ),
        migrations.AlterField(
            model_name="country",
            name="lux_visual_bool",
            field=models.BooleanField(default=False, verbose_name="ЛЮКС/В"),
        ),
        migrations.AlterField(
            model_name="country",
            name="notification_ordinary_bool",
            field=models.BooleanField(
                default=False, verbose_name="УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ"
            ),
        ),
        migrations.AlterField(
            model_name="country",
            name="notification_urgent_bool",
            field=models.BooleanField(
                default=False, verbose_name="УВЕДОМЛЕНИЕ ТЕЛЕГРАФОМ СРОЧНОЕ"
            ),
        ),
        migrations.AlterField(
            model_name="country",
            name="todate_bool",
            field=models.BooleanField(default=True, verbose_name="ВРУЧИТЬ"),
        ),
    ]