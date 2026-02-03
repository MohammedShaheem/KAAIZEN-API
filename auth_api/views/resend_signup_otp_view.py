from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from ..serializers import ResendSignupOTPSerializer
from ..services.otp.signup_otp_service import resend_signup_otp


class ResendSignupOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendSignupOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        resend_signup_otp(email)

        return Response(
            {"detail": "OTP resent to your email"},
            status=status.HTTP_200_OK
        )
