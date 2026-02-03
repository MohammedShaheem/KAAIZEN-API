from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from ..serializers import VerifyOTPSerializer
from ..services.auth.signup_verify_service import (
    verify_and_create_user,
    InvalidOTPError,
    SignupSessionExpiredError,
    SignupVerificationError
)
from ..services.auth.jwt_cookie_service import set_jwt_cookies


class VerifySignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            serializer = VerifyOTPSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data["email"]
            otp = serializer.validated_data["otp"]

            user, refresh = verify_and_create_user(email, otp)

            response = Response(
                {
                    "user": {
                        "email": user.email,
                        "role": user.role,
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

        except InvalidOTPError as e:
            return Response(
                {
                    "error": {
                        "code": "INVALID_OTP",
                        "message": str(e),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except SignupSessionExpiredError as e:
            return Response(
                {
                    "error": {
                        "code": "SESSION_EXPIRED",
                        "message": str(e),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except SignupVerificationError as e:
            return Response(
                {
                    "error": {
                        "code": "SIGNUP_VERIFY_FAILED",
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
