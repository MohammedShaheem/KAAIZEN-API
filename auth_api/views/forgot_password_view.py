from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from ..serializers import ForgotPasswordSerializer
from ..services.auth.password_reset_service import (
    request_password_reset,
    PasswordResetError
)


class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            serializer = ForgotPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data["email"]

            otp_sent = request_password_reset(email)

            return Response(
                {
                    "detail": "If the email exists, an OTP has been sent",
                    "otp_sent": otp_sent,
                },
                status=status.HTTP_200_OK
            )

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

        except PasswordResetError as e:
            return Response(
                {
                    "error": {
                        "code": "OTP_REQUEST_FAILED",
                        "message": str(e),
                    }
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
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
