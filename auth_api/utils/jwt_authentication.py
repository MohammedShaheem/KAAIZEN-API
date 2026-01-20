from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


AUTH_EXEMPT_PATHS = [
    "/api/auth/login/",
    "/api/auth/signup/",
    "/api/auth/refresh/",
]

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        if request.path in AUTH_EXEMPT_PATHS:
            return None
        
        raw_token = request.COOKIES.get("access")
       
        print("entering here")
        print("token",raw_token)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            print("user:",user)
            return(user, validated_token)

        except Exception as e:
            print("AUTH ERROR:", e)
            raise AuthenticationFailed("Invalid or expired token")
