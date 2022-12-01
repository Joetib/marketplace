from django.urls import path
from . import views
from allauth.account.views import LogoutView

urlpatterns = [
    path("receive-marketplace-subscription/", views.receive_marketplace_subscription, name="receive_marketplace_subscription"),
    path("login/<int:customer_pk>/", views.login_view, name="account_login"),
    path("login/", views.login_view, name="account_login"),
    path("register/<int:customer_pk>/", views.register_view, name="account_signup"),
    path("register/", views.register_view, name="account_signup"),
    path("action/", views.action, name="action"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout", LogoutView.as_view(), name="account_logout"),

]