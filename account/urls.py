from django.urls import path
from .views import *

urlpatterns = [
    # Authentication
    path("auth/signup/", SignUpView.as_view(), name="auth_signup"),
    path("auth/login/", LoginView.as_view(), name="auth_login"),
    path("auth/profile/", ProfileView.as_view(), name="auth_profile"),
    path("auth/changeprofile/", ProfileView.as_view(), name="auth_changeprofile"),
    # Account Varifications
    path("auth/emailverify/", EmailVerification.as_view(), name="auth_emailverify"),
    path("activate/<uidb64>/<token>", ActivateAccount.as_view(), name="activate"),
    # Forget password
    path(
        "auth/forget_password/",
        ForgetPasswordView.as_view(),
        name="auth_forget_password",
    ),
    path(
        "auth/otp_verify/",
        ForgetPasswordView.as_view(),
        name="auth_otp_verify",
    ),
    path(
        "auth/update_password/",
        ForgetPasswordView.as_view(),
        name="auth_otp_update_password",
    ),
]
