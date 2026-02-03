from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from ..services.auth.google_auth_service import handle_google_auth,GoogleAuthError
from ..services.auth.jwt_cookie_service import set_jwt_cookies


class GoogleAuthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            token = request.data.get("id_token")

            user, refresh, has_profile = handle_google_auth(token)

            response = Response(
                {
                    "user": {
                        "email": user.email,
                        "role": user.role,
                        "has_profile": has_profile,
                    }
                },
                status=status.HTTP_200_OK
            )

            set_jwt_cookies(response, refresh)
            return response

        except GoogleAuthError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
