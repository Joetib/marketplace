from django.urls import path
from . import views
from allauth.account.views import LogoutView

urlpatterns = [
    path("receive-marketplace-subscription/", views.receive_marketplace_subscription, name="receive_marketplace_subscription"),
    path("register/<slug:customer_id>/", views.register_view, name="account_signup"),
    path("register/", views.register_view, name="account_signup"),
    path("action/", views.action, name="action"),
    path("thank-you/", views.thank_you, name="thank_you"),

]