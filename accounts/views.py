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

# Create your views here.


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
    
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST, instance=customer)
        if register_form.is_valid():
            cd = register_form.cleaned_data
            customer: Customer = register_form.save()
            messages.success(request, "Account created successfully.")
            return redirect(
                reverse("thank_you")
            )

        messages.error(request, "Please fix the errors in the form and try again.")
        print("Errors : ", register_form.fields['phone_number'].error_messages)
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
