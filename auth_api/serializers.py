from rest_framework import serializers
from django.contrib.auth import get_user_model


user = get_user_model()


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    # role = serializers.CharField()
    
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp  = serializers.CharField(min_length=6, max_length=6)
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)
    login_as = serializers.ChoiceField(choices=["client", "trainer", "admin"])

    

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    

class VerifyResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_token = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(min_length=6)
    
class ResendResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()