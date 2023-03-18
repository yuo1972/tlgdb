# Generated by Django 4.1.5 on 2023-03-13 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reestr", "0018_record_country"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="email",
            field=models.EmailField(
                default=None, max_length=254, verbose_name="электронная почта"
            ),
        ),
    ]