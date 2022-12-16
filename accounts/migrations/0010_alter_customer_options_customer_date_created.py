# Generated by Django 4.1.3 on 2022-12-16 15:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0009_alter_customer_phone_number_alter_customer_title"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="customer",
            options={"ordering": ("date_created",)},
        ),
        migrations.AddField(
            model_name="customer",
            name="date_created",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(
                    2022, 12, 16, 15, 39, 50, 846434, tzinfo=datetime.timezone.utc
                ),
            ),
            preserve_default=False,
        ),
    ]
