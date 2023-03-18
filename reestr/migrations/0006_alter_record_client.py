# Generated by Django 4.1.5 on 2023-03-02 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("reestr", "0005_alter_record_client_alter_record_tlg"),
    ]

    operations = [
        migrations.AlterField(
            model_name="record",
            name="client",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="client_records",
                to="reestr.client",
            ),
        ),
    ]