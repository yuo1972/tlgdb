# Generated by Django 4.1.5 on 2023-03-15 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reestr", "0027_alter_record_cost_alter_record_cost_nds_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="record",
            name="cost_notif",
            field=models.FloatField(default=0, verbose_name="Уведомление о вручении"),
        ),
    ]
