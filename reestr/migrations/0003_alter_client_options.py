# Generated by Django 4.1.5 on 2023-03-02 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reestr", "0002_alter_client_unique_together_alter_client_code_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="client",
            options={"verbose_name_plural": "Клиенты"},
        ),
    ]
