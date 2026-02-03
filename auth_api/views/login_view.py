from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from ..serializers import LoginSerializer
from ..services.auth.login_service import (
    login_user,
    InvalidCredentialsError,
    RoleMismatchError,
    LoginError
)
from ..services.auth.jwt_cookie_service import set_jwt_cookies


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            login_as = serializer.validated_data["login_as"]

            user, refresh, has_profile = login_user(
                request=request,
                email=email,
                password=password,
                login_as=login_as
            )

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

        except ValidationError as e:
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": e.detail,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except InvalidCredentialsError as e:
            return Response(
                {
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": str(e),
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        except RoleMismatchError as e:
            return Response(
                {
                    "error": {
                        "code": "ROLE_MISMATCH",
                        "message": str(e),
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )

        except LoginError as e:
            return Response(
                {
                    "error": {
                        "code": "LOGIN_FAILED",
                        "message": str(e),
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception:
            return Response(
                {
                    "error": {
                        "code": "SERVER_ERROR",
                        "message": "Internal server error",
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
