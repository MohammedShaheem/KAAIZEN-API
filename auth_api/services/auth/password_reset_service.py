from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from ..otp.reset_otp_service   import (
    send_reset_otp,
    verify_reset_otp,
    verify_reset_token,
    clear_reset_data
)

User = get_user_model()


class PasswordResetError(Exception):
    pass


class ResetOTPError(PasswordResetError):
    pass


class ResetTokenError(PasswordResetError):
    pass


class UserNotFoundError(PasswordResetError):
    pass


class SamePasswordError(PasswordResetError):
    pass


def request_password_reset(email: str):
    """
    sends OTP if user exists.
    returns: otp_sent
    """

    try:
        user = User.objects.filter(email=email).first()

        if not user:
            return False

        send_reset_otp(email)
        return True

    except Exception as e:
        raise PasswordResetError("Too many OTP requests or service unavailable") from e


def verify_reset_otp_service(email: str, otp: str):
    """
    verifies OTP and returns reset token.
    returns: reset_token
    """

    try:
        reset_token = verify_reset_otp(email, otp)

        if not reset_token:
            raise ResetOTPError("Invalid or expired OTP")

        return reset_token

    except ResetOTPError:
        raise

    except Exception as e:
        raise PasswordResetError("Failed to verify OTP") from e


def reset_password_service(email: str, reset_token: str, new_password: str):
    """
    Resets user password.
    """

    try:
        if not verify_reset_token(email, reset_token):
            raise ResetTokenError("Invalid or expired reset token")

        user = User.objects.filter(email=email).first()
        if not user:
            raise UserNotFoundError("User not found")

        if check_password(new_password, user.password):
            raise SamePasswordError("New password cannot be the same as old password")

        user.set_password(new_password)
        user.save()

        clear_reset_data(email)

    except (ResetTokenError, UserNotFoundError, SamePasswordError):
        raise

    except Exception as e:
        raise PasswordResetError("Failed to reset password") from e
