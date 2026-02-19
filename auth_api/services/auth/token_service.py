from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.conf import settings


class TokenRefreshError(Exception):
    pass


def refresh_access_token(refresh_token: str):
    """
    validates refresh token, checks blacklist, and returns new access token.
    """

    if not refresh_token:
        raise TokenRefreshError("No refresh token")

    try:
        refresh_obj = RefreshToken(refresh_token)

        jti = refresh_obj.get("jti")
        if settings.REDIS_CLIENT.exists(f"blacklist:{jti}"):
            raise TokenRefreshError("Token revoked")

        return str(refresh_obj.access_token)

    except TokenError:
        raise TokenRefreshError("Invalid or expired refresh token")

    except Exception:
        raise TokenRefreshError("Failed to refresh access token")
