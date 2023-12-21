from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import USER_STATUS, CustomUser, UserProfile
from .serializers import SignUpSerializer, UserProfileSerializer, UserSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token import account_activation_token
from django.core.mail import send_mail
from .utlls import Utills
import pdb


# Create your views here.
class SignUpView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "payload": serializer.data,
                    "message": "You have Succesfully signed up!",
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        payload = {}
        user = None

        email = request.data["email"]
        password = request.data["password"]

        user = CustomUser.get_user_by_email(email=email)

        if user is None:
            raise AuthenticationFailed("User not found!")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password!")

        payload = {
            "uid": user.id,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "message": "You have successfully Logged In!",
        }

        return Response(payload, status=status.HTTP_200_OK)


class ProfileView(APIView):
    def get(self, request, *args, **kwargs):
        uid = None
        user = None
        payload = {}

        uid = request.headers.get("uid")
        user = CustomUser.get_user(id=uid)

        userSerializer = UserSerializer(user)
        profleSerialozer = UserProfileSerializer(user.user_profile)

        payload = {
            "user": userSerializer.data,
            "profile": profleSerialozer.data,
        }
        return Response(payload, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        uid = None
        user = None
        uid = request.headers.get("uid")

        if uid is not None:
            user = CustomUser.get_user(id=uid)
            user.status = USER_STATUS[1][0]
            user.save()

            userSerializer = UserSerializer(user)
            profleSerialozer = UserProfileSerializer(
                user.user_profile, data=request.data
            )

            profleSerialozer.is_valid(raise_exception=True)

            profleSerialozer.save()
        else:
            payload = {"errors": {"message": "User not found!"}}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

        payload = {
            "user": userSerializer.data,
            "profile": profleSerialozer.data,
            "message": "Profile saved successfully!",
        }
        return Response(payload, status=status.HTTP_204_NO_CONTENT)


class EmailVerification(APIView):
    def get(self, request):
        payload = {}
        email = request.data.get("email")
        user = CustomUser.get_user_by_email(email=email)
        if user is not None:
            current_site = get_current_site(request)
            mail_subject = "Activate your account."
            message = render_to_string(
                "account/acc_active_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            try:
                send_mail(
                    subject=mail_subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
                payload = {
                    "message": "Verification link has been sent to your Email ID!"
                }
                return Response(payload, status=status.HTTP_200_OK)
            except:
                payload = {"message": "Error Occured In Sending Mail, Try Again!"}
                return Response(payload, status=status.HTTP_404_NOT_FOUND)
        else:
            payload = {"message": "you are not registered with this email!"}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)


class ActivateAccount(APIView):
    def get(self, request, uidb64, token):
        payload = {}
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist) as e:
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            userSerializer = UserSerializer(user)
            payload = {
                "user": userSerializer.data,
                "message": "Profile saved successfully!",
            }
            return Response(payload, status=status.HTTP_200_OK)
        else:
            payload = {
                "errors": {
                    "message": "Activation link is invalid or your account is already Verified! Try To Login!",
                }
            }
            return Response(payload, status=status.HTTP_200_OK)


class ForgetPasswordView(APIView):
    def get(self, request):
        payload = {}
        email = request.data.get("email")
        obj = Utills()
        otp = obj.get_otp(6)
        # print(f"otp:--{otp}")
        user = CustomUser.get_user_by_email(email=email)
        if user is not None:
            current_site = get_current_site(request)
            mail_subject = "Forget Password"
            message = render_to_string(
                "account/otp_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "otp": otp,
                },
            )
            try:
                send_mail(
                    subject=mail_subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
                payload = {
                    "message": "Verification Code has been sent to your email!",
                    "otp": otp,
                }
                return Response(payload, status=status.HTTP_200_OK)
            except:
                payload = {"message": "Error Occured In Sending Mail, Try Again!"}
                return Response(payload, status=status.HTTP_404_NOT_FOUND)
        else:
            payload = {"message": "you are not registered with this email!"}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        payload = {}
        generated_otp = int(request.headers.get("oldotp"))
        # print(f"generated_otp:-{type(generated_otp)}")
        otp = request.data.get("otp")
        # print(f"newotp:-{type(otp)}")

        if generated_otp == otp:
            payload = {
                "message": "Your verification is done. Now you can change your password!"
            }
            return Response(payload, status=status.HTTP_200_OK)
        else:
            payload = {"message": "you have entered invalid otp!"}
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        uid = None
        user = None
        payload = {}
        password = request.data.get("password")
        cpassword = request.data.get("cpassword")
        if password == cpassword:
            uid = request.headers.get("uid")
            user = CustomUser.get_user(id=uid)
            if user is not None:
                user.set_password(password)
                user.save()
                payload = {"message": "your Password has successfully changed!"}
                return Response(payload, status=status.HTTP_204_NO_CONTENT)
            else:
                payload = {"errors": {"message": "User not found!"}}
                return Response(payload, status=status.HTTP_404_NOT_FOUND)
        else:
            payload = {
                "errors": {"message": "Password and Confirm Password must be same!"}
            }
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
