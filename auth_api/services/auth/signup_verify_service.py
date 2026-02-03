from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from ..otp.signup_otp_service import verify_signup_otp,get_temp_signup_data,delete_temp_signup_data


User = get_user_model()


class SignupVerificationError(Exception):
    pass


class InvalidOTPError(SignupVerificationError):
    pass


class SignupSessionExpiredError(SignupVerificationError):
    pass


def verify_and_create_user(email: str, otp: str):
    """
    verifies OTP, creates user, and issues JWT tokens.
    returns: (user, refresh_token)
    """

    try:
        if not verify_signup_otp(email, otp):
            raise InvalidOTPError("Invalid or expired OTP")

        temp_user = get_temp_signup_data(email)
        if not temp_user:
            raise SignupSessionExpiredError("Signup session expired")

        with transaction.atomic():
            user = User.objects.create_user(
                email=temp_user["email"],
                password=temp_user["password"],
                role=temp_user["role"],
                is_active=True,
            )

            delete_temp_signup_data(email)

            refresh = RefreshToken.for_user(user)

            return user, refresh

    except (InvalidOTPError, SignupSessionExpiredError):
        raise

    except Exception as e:
        raise SignupVerificationError("Failed to verify signup") from e
