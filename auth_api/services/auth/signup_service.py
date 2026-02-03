from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status

from ..otp.signup_otp_service import send_signup_otp,store_temp_signup_data

User = get_user_model()


class SignupError(Exception):
    pass


class UserAlreadyRegisteredError(SignupError):
    pass


class UserBlockedError(SignupError):
    pass


def signup_with_role(email: str, password: str, role: str):
    

    try:
        user = User.objects.filter(email=email).first()

        if user:
            if user.is_active:
                raise UserAlreadyRegisteredError("User already registered")
            else:
                raise UserBlockedError("Blocked user")

        store_temp_signup_data(email, password, role)
        send_signup_otp(email)

    except (UserAlreadyRegisteredError, UserBlockedError):
        raise

    except Exception as e:
        raise SignupError("Signup process failed") from e