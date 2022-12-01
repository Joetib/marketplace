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

# Create your views here.


def receive_marketplace_subscription(request: HttpRequest):
    data: dict = request.POST
    registration_token: str = data.get("x-amzn-marketplace-token", "")
    if registration_token:
        marketplace_client = boto3.client('meteringmarketplace')
        customer_data: dict = marketplace_client.resolve_customer(registration_token)
        print(customer_data)
        product_code: str = customer_data["ProductCode"]
        customerID: str = customer_data["CustomerIdentifier"]
        customer_aws_account_id: str = customer_data["CustomerAWSAccountId"]
        customer: Customer = Customer.objects.get_or_create(
            product_code=product_code,
            customerID=customerID,
            customer_aws_account_id=customer_aws_account_id,
        )[0]

        return redirect(reverse("account_login", kwargs={"customer_pk": customer.pk}))
    raise Http404(f"Account setup failed for registration token: {registration_token}")


def login_view(request: HttpRequest, customer_pk: Optional[int] = None):
    if request.method == "POST":
        login_form = forms.LoginForm(request.POST)
        if login_form.is_valid():
            cd = login_form.cleaned_data
            user: Optional[CustomUser] = authenticate(
                request, email=cd["email"], password=cd["password"]
            )
            if user:
                if customer_pk:
                    customer: Customer = get_object_or_404(Customer, pk=customer_pk)

                    customer.user = user
                    customer.save()
                user.refresh_from_db()

                login(request, user)
                return redirect("dashboard")
            messages.error(request, "Invalid Credentials")
        messages.error(request, "Please fix the errors in the form and try again.")
    else:
        login_form = forms.LoginForm()
    return render(
        request,
        "account/login.html",
        context={"form": login_form, "customer": customer_pk},
    )


def register_view(request: HttpRequest, customer_pk: Optional[int] = None):
    if not customer_pk:
        messages.warning(request, "Please use the AWS portal to begin registration process")
        return redirect("account_login")
    customer: Customer = get_object_or_404(Customer, pk=customer_pk)
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        if register_form.is_valid():
            cd = register_form.cleaned_data
            user: CustomUser = register_form.save()
            customer.user = user
        
            user.set_password(cd["password"])
            customer.save()
            return redirect(
                reverse("account_login", kwargs={"customer_pk": customer.pk})
            )

        messages.error(request, "Please fix the errors in the form and try again.")
    else:
        register_form = forms.RegisterForm()
    return render(
        request,
        "account/login.html",
        context={"form": register_form, "customer": customer},
    )
@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "account/action.html",)

@login_required
def action(request: HttpRequest) -> HttpResponse:
    customer = request.user.get_customer()
    if customer:
        number: int = int(request.GET.get("number_of_times", 1))

        activity = Activity.objects.create(number=number, customer=customer)
        messages.success(request, f"Action performed successfully. \n Number of times: {number}.")
    else:
        messages.error(request, f"You do not have a marketplace account associated.")
    return redirect("dashboard")