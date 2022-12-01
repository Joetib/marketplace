from django.http import HttpRequest
from .utils import verify_entitlement
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect


def check_entitlement_middleware(get_response):
    def middleware(request: HttpRequest):
        if request.user.is_authenticated and request.path == reverse("action"):
            if not any(
                [verify_entitlement(i) for i in request.user.subscriptions.all()]
            ):
                messages.error(request, "You cannot perform the action because you do not have an active subscription.")
                return redirect("dashboard")
        response = get_response(request)
        return response

    return middleware
