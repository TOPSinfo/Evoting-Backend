from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("email", "is_staff", "is_active", "status", "is_approved")
    list_filter = (
        "status",
        "is_staff",
        "is_active",
        "is_approved",
    )
    fieldsets = (
        (None, {"fields": ("email", "full_name", "password", "status", "created_by")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_approved",
                    "groups",
                    "user_permissions",
                    # "custom_permissions",
                )
            },
        ),  #'is_customer' , 'is_seller'
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_approved",
                    "status",
                    "created_by",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


class ProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    list_display = ("user", "voter_id", "aadhar_no", "address")


# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(UserPermissions)
