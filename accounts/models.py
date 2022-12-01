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
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL, related_name="subscriptions")
    product_code = models.TextField(max_length=255, blank=False, null=False)
    customerID = models.TextField(max_length=255, blank=False, null=False)
    customer_aws_account_id = models.TextField(max_length=100, blank=False, null=False)

    def __str__(self):
        return f"Customer: {self.customerID}"
    
    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

class Activity(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    number = models.PositiveIntegerField(default=1)
    charged = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name="activities")