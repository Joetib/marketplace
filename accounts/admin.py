from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Customer, Activity

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username',]

    fieldsets = [
        *UserAdmin.fieldsets,
    ]
    #readonly_fields = ['ruser', 'referral_code']
    fieldsets.insert(
        2,
        (
            None,
            {
                "fields": (
                    "phone_number",
                )
            }
        )
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Customer)
admin.site.register(Activity)