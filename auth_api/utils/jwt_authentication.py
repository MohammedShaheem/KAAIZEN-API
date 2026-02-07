from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import logging


logger = logging.getLogger(__name__)

AUTH_EXEMPT_PATHS = [
    "/api/auth/client_signup/",
    "/api/auth/trainer_signup/",
    "/api/auth/login/",
    "/api/auth/refresh/",
]

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        if request.path in AUTH_EXEMPT_PATHS:
            return None
        logger.info(f"from cookiejwtauthentication:{request.data}")
        
        raw_token = request.COOKIES.get("access")
       
        
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return(user, validated_token)

        except Exception as e:
            raise AuthenticationFailed("Invalid or expired token")
