# Generated by Django 4.1.5 on 2023-03-15 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reestr", "0025_alter_record_cost_todate"),
    ]

    operations = [
        migrations.AlterField(
            model_name="record",
            name="cost_service",
            field=models.FloatField(default=0, verbose_name="Платный запрос"),
        ),
    ]
