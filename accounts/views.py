from typing import Optional
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, Http404
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
import boto3
import urllib.parse as urlparse
from .models import CustomUser, Customer, Activity
from django.contrib import messages
from . import forms
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, EmailMessage

# Create your views here.


def send_customer_registration_email(customer: Customer, new_registered=True):
    """Send an email to the administrator on the regitration of a customer

    new_registered: denotes whether this is a new account registration or an update to
        an existing account registration

    """
    subscription_clause = (
        "subscribed" if new_registered else "updated their subscription"
    )
    registration_clause = (
        "A new client has registered"
        if new_registered
        else f"{customer.first_name} has updated their registration details"
    )
    sheet_url = f"https://docs.google.com/spreadsheets/d/{settings.SPREADSHEET_ID}/"
    message = f"""
        {registration_clause} for EdgeIQ services
        Please Find below, the details of their registration

        First Name: {customer.first_name}
        Last Name:  {customer.last_name}
        Email:      {customer.email}
        Company:    {customer.company_name}

        You may see further details about their registration in the google sheet at {sheet_url}.
        """
    # send_mail(
    #     subject=f"AWS Marketplace Subscription.",
    #     message=message,
    #     from_email=settings.DEFAULT_FROM_EMAIL,
    #     recipient_list=settings.DEFAULT_TO_EMAILS,

    # )
    email = EmailMessage(
        subject=f"AWS Marketplace Subscription",
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=settings.DEFAULT_TO_EMAILS,
        cc=settings.DEFAULT_CC_EMAILS,
    )
    email.send(fail_silently=True)


@csrf_exempt
def receive_marketplace_subscription(request: HttpRequest):
    data: dict = request.POST
    registration_token: str = data.get("x-amzn-marketplace-token", "")
    print(registration_token)
    if registration_token:
        try:
            marketplace_client = boto3.client("meteringmarketplace")
            customer_data: dict = marketplace_client.resolve_customer(
                RegistrationToken=registration_token
            )
            product_code: str = customer_data["ProductCode"]
            customerID: str = customer_data["CustomerIdentifier"]
            customer_aws_account_id: str = customer_data["CustomerAWSAccountId"]
            customer: Customer = Customer.objects.get_or_create(
                product_code=product_code,
                customerID=customerID,
                customer_aws_account_id=customer_aws_account_id,
            )[0]
            return redirect(
                reverse("account_signup", kwargs={"customer_id": customer.customerID})
            )
        except Exception as e:
            messages.error(request, str(e))
            print(e)
    messages.error(
        request, f"Account setup failed for registration token: {registration_token}"
    )
    print("Account verification failed.")
    return redirect("account_signup")


def register_view(request: HttpRequest, customer_id: Optional[str] = None):
    if not customer_id:
        messages.warning(
            request, "Please use the AWS portal to begin registration process"
        )
        return redirect("home")

    customer: Customer = get_object_or_404(Customer, customerID=customer_id)

    already_complete_account = customer.is_registration_complete()
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST, instance=customer)
        if register_form.is_valid():
            cd = register_form.cleaned_data
            customer: Customer = register_form.save()
            if not already_complete_account:
                messages.success(request, "Account created successfully.")
                send_customer_registration_email(customer=customer, new_registered=True)
            else:
                messages.success(request, "Account Updated successfully.")
                send_customer_registration_email(
                    customer=customer, new_registered=False
                )

            return redirect(reverse("thank_you"))

        messages.error(request, "Please fix the errors in the form and try again.")
        print("Errors : ", register_form.fields["phone_number"].error_messages)
        print("Errors as text: ", register_form.errors.as_data())
    else:
        register_form = forms.RegisterForm(instance=customer)
    return render(
        request,
        "account/signup.html",
        context={"form": register_form, "customer": customer},
    )


def thank_you(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "account/thank_you.html",
    )


@login_required
def action(request: HttpRequest) -> HttpResponse:
    customer = request.user.get_customer()
    if customer:
        number: int = int(request.GET.get("number_of_times", 1))

        activity = Activity.objects.create(number=number, customer=customer)
        messages.success(
            request, f"Action performed successfully. \n Number of times: {number}."
        )
    else:
        messages.error(request, f"You do not have a marketplace account associated.")
    return redirect("dashboard")
