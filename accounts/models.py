from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.email

    def get_customer(self):
        try:
            return self.subscriptions.first()
        except:
            return None


class Customer(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)

    product_code = models.CharField(max_length=255, blank=False, null=False)
    customerID = models.CharField(max_length=255, blank=False, null=False)
    customer_aws_account_id = models.TextField(max_length=100, blank=False, null=False)
    dimension = models.CharField(max_length=100, blank=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=1)

    title = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=16, blank=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ("date_created",)

    def __str__(self):
        return f"Customer: {self.customerID}"

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

    def is_registration_complete(self):
        return (
            self.email
            and self.first_name
            and self.last_name
            and self.phone_number
            and self.customerID
            and self.company_name
        )


class Activity(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    number = models.PositiveIntegerField(default=1)
    charged = models.BooleanField(default=False)
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, related_name="activities"
    )
