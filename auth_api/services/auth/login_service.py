from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from clients.models import ClientProfile
from trainers.models import TrainerProfile


class LoginError(Exception):
    pass


class InvalidCredentialsError(LoginError):
    pass


class RoleMismatchError(LoginError):
    pass


def login_user(request, email: str, password: str, login_as: str):
    """
    authenticates user, validates role, checks profile, and issues JWT
    returns: (user, refresh_token, has_profile)
    """

    try:
        user = authenticate(request, username=email, password=password)

        if user is None:
            raise InvalidCredentialsError("Invalid credentials")

        if user.role != login_as:
            raise RoleMismatchError(
                f"You are registered as a {user.role}. "
                f"You cannot log in as a {login_as}."
            )

        if user.role == "client":
            has_profile = ClientProfile.objects.filter(user=user).exists()
        elif user.role == "trainer":
            has_profile = TrainerProfile.objects.filter(user=user).exists()
        else:
            has_profile = False

        refresh = RefreshToken.for_user(user)

        return user, refresh, has_profile

    except (InvalidCredentialsError, RoleMismatchError):
        raise

    except Exception as e:
        raise LoginError("Login process failed") from e
