from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..services.auth.token_service import refresh_access_token,TokenRefreshError


class RefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh")

            new_access_token = refresh_access_token(refresh_token)

            response = Response(
                {"detail": "Token refreshed"},
                status=status.HTTP_200_OK
            )

            response.set_cookie(
                key="access",
                value=new_access_token,
                httponly=True,
                secure=False,   
                samesite="Lax",
                max_age=60 * 15,
                path="/"
            )

            return response

        except TokenRefreshError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

        except Exception:
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
