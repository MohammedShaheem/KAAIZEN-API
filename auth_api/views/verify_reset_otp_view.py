from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from ..serializers import VerifyResetOTPSerializer
from ..services.auth.password_reset_service import (
    verify_reset_otp_service,
    ResetOTPError,
    PasswordResetError
)


class VerifyResetOTPView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            serializer = VerifyResetOTPSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data["email"]
            otp = serializer.validated_data["otp"]

            reset_token = verify_reset_otp_service(email, otp)

            return Response(
                {
                    "detail": "OTP verified. Use the token to reset password.",
                    "reset_token": reset_token,
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

        except ResetOTPError as e:
            return Response(
                {
                    "error": {
                        "code": "INVALID_OTP",
                        "message": str(e),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except PasswordResetError as e:
            return Response(
                {
                    "error": {
                        "code": "OTP_VERIFY_FAILED",
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
