from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model,authenticate
from rest_framework.permissions import AllowAny
import logging

from ..services.auth.signup_service import signup_with_role
from ..serializers import SignupSerializer



logger = logging.getLogger(__name__)
User = get_user_model()


class ClientSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        
        logger.info(f"from clientsignupview:{request.data}")
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        signup_with_role(
            email=email,
            password=password,
            role="client"
        )

        return Response(
            {"detail": "OTP sent to your email"},
            status=status.HTTP_200_OK
        )
