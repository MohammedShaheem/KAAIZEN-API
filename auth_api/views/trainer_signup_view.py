from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.exceptions import ValidationError

from ..services.auth.signup_service import (
    signup_with_role,
    UserAlreadyRegisteredError,
    UserBlockedError,
    SignupError
)
from ..serializers import SignupSerializer


class TrainerSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = SignupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            signup_with_role(
                email=email,
                password=password,
                role="trainer"
            )

            return Response(
                {"detail": "OTP sent to your email"},
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

        except UserAlreadyRegisteredError as e:
            return Response(
                {
                    "error": {
                        "code": "USER_EXISTS",
                        "message": str(e),
                    }
                },
                status=status.HTTP_409_CONFLICT
            )

        except UserBlockedError as e:
            return Response(
                {
                    "error": {
                        "code": "USER_BLOCKED",
                        "message": str(e),
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )

        except SignupError as e:
            return Response(
                {
                    "error": {
                        "code": "SIGNUP_FAILED",
                        "message": str(e),
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )