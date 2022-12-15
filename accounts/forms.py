from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Customer
import secrets
class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username',)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username',)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"


class LoginForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("email", "password")

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("email",  "first_name", "last_name", "title", "company_name", "phone_number", )
