# Generated by Django 4.1.5 on 2023-03-15 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reestr", "0026_alter_record_cost_service"),
    ]

    operations = [
        migrations.AlterField(
            model_name="record",
            name="cost",
            field=models.FloatField(default=0, verbose_name="Стоимость телеграммы"),
        ),
        migrations.AlterField(
            model_name="record",
            name="cost_nds",
            field=models.FloatField(
                default=0, verbose_name="Стоимость телеграммы с НДС"
            ),
        ),
        migrations.AlterField(
            model_name="record",
            name="kkv_bool",
            field=models.BooleanField(
                default=False, verbose_name="Платный запрос (флаг)"
            ),
        ),
        migrations.AlterField(
            model_name="record",
            name="num_word",
            field=models.IntegerField(default=0, verbose_name="Количество слов"),
        ),
        migrations.AlterField(
            model_name="record",
            name="todate_bool",
            field=models.BooleanField(
                default=False, verbose_name="Вручить в срок (флаг)"
            ),
        ),
    ]
