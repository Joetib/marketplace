# Generated by Django 4.1.3 on 2022-12-09 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_customer_dimension_customer_value"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="expiry_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]