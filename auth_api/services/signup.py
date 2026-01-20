from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from ..otp_service import store_temp_signup_data,send_singup_otp


User = get_user_model()

def signup_with_role(email, password, role):
    user = User.objects.filter(email=email).first()
    
    if user:
        if user.is_active:
            return Response(
                {"detail": "User already registered"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"detail": "Blocked user"},
            status=status.HTTP_403_FORBIDDEN
        )
        
    store_temp_signup_data(email, password, role)
    send_singup_otp(email)
        
    return Response(
        {"detail": "OTP sent to your email"},
        status=status.HTTP_200_OK
    )