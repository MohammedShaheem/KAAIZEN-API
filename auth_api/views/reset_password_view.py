from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from ..serializers import ResetPasswordSerializer
from ..services.auth.password_reset_service import (
    reset_password_service,
    ResetTokenError,
    UserNotFoundError,
    SamePasswordError,
    PasswordResetError
)


class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            serializer = ResetPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data["email"]
            reset_token = serializer.validated_data["reset_token"]
            new_password = serializer.validated_data["new_password"]

            reset_password_service(email, reset_token, new_password)

            return Response(
                {"detail": "Password reset successfully. Please log in"},
                status=status.HTTP_200_OK
            )

        except ValidationError as e:
            print("VALIDATION ERROR:", e)
            return Response(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": e.detail,
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except ResetTokenError as e:
            print("Token ERROR:", e)
            return Response(
                {
                    "error": {
                        "code": "INVALID_RESET_TOKEN",
                        "message": str(e),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except UserNotFoundError as e:
            return Response(
                {
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "message": str(e),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except SamePasswordError as e:
            print("same password:", e)
            return Response(
                {
                    "error": {
                        "code": "SAME_PASSWORD",
                        "message": str(e),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except PasswordResetError as e:
            return Response(
                {
                    "error": {
                        "code": "RESET_FAILED",
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
