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
        model = CustomUser
        fields = ("email", "password", "first_name", "last_name")

    def save(self, *args, **kwargs):
        email: str = self.cleaned_data["email"]
        username = email.split("@")[0].replace(".", "_") + "_" + secrets.token_urlsafe(3)
        self.instance.username = username
        return super().save(*args, **kwargs)