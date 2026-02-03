from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..services.otp.resend_otp_service import resend_reset_otp
from ..serializers import ResendResetOTPSerializer


class ResendResetOTPView(APIView):
    def post(self,request):
        serializer = ResendResetOTPSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # serializer.is_valid(raise_exception=True) 
        
        email = serializer.validated_data['email']
        
        try:
            resend_reset_otp(email)
        except Exception as e:
            return Response(
                {"detiail":str(e)},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        return Response(
            {"detail":"OTP resent successfully"},
            status=status.HTTP_200_OK
        )