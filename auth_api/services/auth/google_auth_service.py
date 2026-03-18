from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError

from users.models import User
from clients.models import ClientProfile
from trainers.models import TrainerProfile

from .jwt_cookie_service import set_jwt_cookies
from ...utils.google import verify_google_token


class GoogleAuthError(Exception):
    pass


def handle_google_auth(id_token: str):
    """
    handles full google authentication flow.
    returns:user,refresh_token,has_profile
    """

    if not id_token:
        raise GoogleAuthError("Token missing")

    payload = verify_google_token(id_token)
    if not payload:
        raise GoogleAuthError("Invalid Google token")

    google_id = payload.get("sub")
    email = payload.get("email")

    if not google_id or not email:
        raise GoogleAuthError("Google payload incomplete")

    try:
        with transaction.atomic():
            user = User.objects.filter(google_id=google_id).first()

            if not user:
                user = User.objects.filter(email=email).first()

                if user:
                    user.google_id = google_id
                    user.is_verified = True
                    user.save()
                else:
                    user = User.objects.create(
                        email=email,
                        google_id=google_id,
                        is_verified=True,
                    )
                    user.set_unusable_password()
                    user.save()

            if user.role == "client":
                has_profile = ClientProfile.objects.filter(user=user).exists()
            elif user.role == "trainer":
                has_profile = TrainerProfile.objects.filter(user=user).exists()
            else:
                has_profile = False

            refresh = RefreshToken.for_user(user)

            return user, refresh, has_profile

    except Exception as e:
        print("GOOGLE AUTH ERROR:", str(e))   
        import traceback
        traceback.print_exc()                 
        raise GoogleAuthError(str(e))         
