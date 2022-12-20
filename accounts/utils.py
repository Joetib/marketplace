import datetime
import boto3
from .models import Customer, Activity
from django.utils import timezone
from django.conf import settings
from django.db.models.query import QuerySet
from django.core.paginator import Paginator
import time

def update_customer_entitlement(customer: Customer):
    entitlements = get_entitlement(customer)
    print(entitlements)
    if len(entitlements)== 0:
        customer.value = 0
        customer.dimension = ''
    else:
        entitlement = entitlements[-1]
        customer.dimension = entitlement['Dimension']
        value: dict = entitlement["Value"]
        customer.value = list(value.values())[-1] if len(value.values()) > 0 else 0
        customer.expiry_date = entitlement["ExpirationDate"]
    customer.save()

def get_entitlement(customer: Customer) -> list[dict]:
    marketplaceClient = boto3.client("marketplace-entitlement")
    entitlement = marketplaceClient.get_entitlements(
        **{
            "ProductCode": settings.AWS_MARKETPLACE_PRODUCT_KEY,
            "Filter": {
                "CUSTOMER_IDENTIFIER": [
                    customer.customerID,
                ]
            },
            "MaxResults": 25,
        }
    )
    entitlements = entitlement.get("Entitlements", [])
    return entitlements

def verify_entitlement(customer: Customer) -> bool:
    print("verifying")
    

    # Filter entitlements for a specific customerID
    #
    # productCode is supplied after the AWS Marketplace Ops team has published
    # the product to limited
    #
    # customerID is obtained from the ResolveCustomer response
    entitlements = get_entitlement(customer=customer)
    return any(
        [
            i["ExpirationDate"] > timezone.now() 
            for i in entitlements
        ]
    )


def generate_bill(customers: QuerySet[Customer]):
    usageRecords: list[dict] = []
    timestamp = timezone.now()
    for customer in customers:
        activities = Activity.objects.filter(
            customer=customer, charged=False, timestamp__lte=timestamp
        )
        total_charge = sum(activities.values_list("number", flat=True))
        print("Customer: ", customer, " Charge: ", total_charge)
        data = {
            "Timestamp": timestamp,
            "CustomerIdentifier": customer.customerID,
            "Dimension": settings.AWS_MARKETPLACE_PRODUCT_DIMENSION,
            "Quantity": total_charge,
        }
        print(data)
        usageRecords.append(data)
    send_charges(usageRecords)
    Activity.objects.filter(
        customer__in=customers, charged=False, timestamp__lte=timestamp
    ).update(charged=True)

    return usageRecords


def send_charges(usageRecords: list[dict]):

    marketplaceClient = boto3.client("meteringmarketplace")

    response = marketplaceClient.batch_meter_usage(
        UsageRecords=usageRecords, ProductCode=settings.AWS_MARKETPLACE_PRODUCT_KEY
    )
    print(response)


def process_charges():
    customers: QuerySet[Customer] = Customer.objects.all()
    paginator = Paginator(customers, 1)
    for i in paginator.page_range:
        page = paginator.get_page(i)

        usageRecord: list[dict] = generate_bill(page.object_list)
    print(usageRecord)
