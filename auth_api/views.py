from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model,authenticate
from .serializers import SignupSerializer,VerifyOTPSerializer,LoginSerializer,ResendResetOTPSerializer
from .serializers import ForgotPasswordSerializer,VerifyResetOTPSerializer,ResetPasswordSerializer
from.otp_service import send_singup_otp,veriy_signup_otp,store_temp_signup_data,get_temp_signup_data,delete_temp_signup_data
from .otp_service import send_reset_otp,verify_reset_otp,verify_reset_token,clear_reset_data,resend_reset_otp
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.contrib.auth.hashers import check_password
from .utils.google import verify_google_token
from.utils.jwt_authentication import CookieJWTAuthentication
from clients.models import ClientProfile
from rest_framework.permissions import AllowAny
from .services.signup import signup_with_role
from trainers.models import TrainerProfile

 
User = get_user_model()


def set_jwt_cookies(response,refresh:RefreshToken, access_max_age:int=60*15, refresh_max_age:int = 60*60*24*7):
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    #access cookie
    response.set_cookie(
        "access",
        access_token,
        max_age=access_max_age,
        httponly=True,
        secure=False,
        samesite="Lax",
        path="/"
    )
    #refersh cookie
    response.set_cookie(
        "refresh",
        refresh_token,
        max_age=refresh_max_age,
        httponly=True,
        secure=False,
        samesite='Lax',
        path="/"
    )
    return response

def blacklist_refresh_token(refresh_token):
    try:
        jti = refresh_token.get_jti()
        expiry = refresh_token.lifetime
        key = f"blacklist:{jti}"
        settings.REDIS_CLIENT.setex(key, expiry.total_seconds(),"true")
        return True
    except Exception:
        return False
    
###########################################################################

class RefreshView(APIView):
    def post(self,request):
        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
            return Response({"detail":"No refresh token"},status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            refresh_obj = RefreshToken(refresh_token)
            if settings.REDIS_CLIENT.exists(f"blacklist:{refresh_obj.get('jti')}"):
                return Response({"detail":"Token revoked"},status=401)
                
            
            new_access_token = str(refresh_obj.access_token)
            
            response = Response(
                {"detail":"Token refreshed"},
                status=status.HTTP_200_OK
            )
            
            response.set_cookie(
                key="access",
                value=new_access_token,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=60*15,
                path="/"
            )
            return response
        
        except TokenError:
            return Response(
                {"detail":"Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )



class MeView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    def get(self,request):
        
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"detail" : "Unauthenticated"},
                status = status.HTTP_401_UNAUTHORIZED
            )
        return Response(
            {
                "user":{
                    "email":request.user.email,
                    "role":request.user.role
                }
            },
            status = status.HTTP_200_OK
        )

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCsrfToken(APIView):
    def get(self,request):
        return JsonResponse({"detail":"CSRF cookie set"})
    

    


#################################################################################
    

class TrainerSignupView(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        return signup_with_role(
            email=email,
            password=password,
            role="trainer"
        )

#################################################################################################################


class ClientSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        return signup_with_role(
            email=email,
            password=password,
            role="client"
        )

##################################################################################################################


class VerifySignupView(APIView):
    def post(self,request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        
        if not veriy_signup_otp(email,otp):
            return Response(
                {"detail":"Invalid or expired OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
       
        temp_user = get_temp_signup_data(email)
        if not temp_user:
            return Response(
                {"detail":"Signup session expired. Please signup again."},
                status = status.HTTP_400_BAD_REQUEST
            )
            
        user = User.objects.create_user(
            email=temp_user["email"],
            password = temp_user["password"],
            role=temp_user["role"],
            is_active = True
        )
        
        delete_temp_signup_data(email)
        refresh = RefreshToken.for_user(user)
        
        resp = Response({
            "user":{
                "email":user.email,
                "role":user.role
            }
        },
        status = status.HTTP_200_OK
        )
        
        set_jwt_cookies(resp,refresh)
        return resp
            
            
class LoginView(APIView):
    def post(self,request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        
        user = authenticate(request,username=email,password=password)
        
        if user is None:
            return Response(
                {"detail":"Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        if user.role == "client":
            has_profile = ClientProfile.objects.filter(user=user).exists()
        elif user.role == "trainer":
            has_profile = TrainerProfile.objects.filter(user=user).exists()
        else:
            has_profile = False

        
        
        refresh = RefreshToken.for_user(user)
        
        resp = Response({
            "user":{
                "email":user.email,
                "role":user.role,
                "has_profile":has_profile,
            }
        },
        status = status.HTTP_200_OK
        )
        set_jwt_cookies(resp,refresh)
        return resp
    

class LogoutView(APIView):
    def post(self,request):
        refresh_token = request.COOKIES.get("refresh")
        if refresh_token:
            try:
                refresh_obj = RefreshToken(refresh_token)
                blacklist_refresh_token(refresh_obj)
            except TokenError:
                pass
        
        response = Response(
            {"detail" : "Successfully logged  out"},
            status=status.HTTP_205_RESET_CONTENT
        )
        response.delete_cookie("access",path="/")
        response.delete_cookie("refresh",path="/")
        
        return response
        
class ForgotPasswordView(APIView):
    def post(self,request):
        serializer = ForgotPasswordSerializer(data = request.data)
        if not serializer.is_valid():
             
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # serializer.is_valid(raise_exception=True)
         
        email = serializer.validated_data["email"]
        
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"detail":"If the email exists, an OTP has been sent",
                 "otp_sent":False},
                status=status.HTTP_200_OK
            )
        
        try:
            send_reset_otp(email)
            return Response(
                {"detail":"OTP send to your email for password reset.",
                 "otp_sent":True},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail":str(e)},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
           
class VerifyResetOTPView(APIView):
    def post(self,request):
        serializer = VerifyResetOTPSerializer(data=request.data)
        if not serializer.is_valid():
           
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        
        reset_token = verify_reset_otp(email,otp)
        if not reset_token:
            return Response(
                {"detail":"Invalid or expired OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {"detail":"OTP verified. Use the token to reset password.","reset_token": reset_token},
            status = status.HTTP_200_OK
        )
        
class ResetPasswordView(APIView):
    def post(self, request):
        
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        reset_token = serializer.validated_data["reset_token"]
        new_password = serializer.validated_data["new_password"]
        
        if not verify_reset_token(email,reset_token):
            return Response(
                {"detail":"Invalid or expired reset token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"detail":"User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if check_password(new_password,user.password):
            return Response(
                {"detail":"New password cannot be the same"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        clear_reset_data(email)
        
        return Response(
            {"detail":"Password reset successfully.Please log in"},
            status=status.HTTP_200_OK
        )
   
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
        
class GoogleAuthView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny]
    def post(self,request):
        token = request.data.get("id_token")
        if not token:
            return Response({"detail":"Token missing"},status=400)
        
        payload = verify_google_token(token)
        if not payload:
            return Response({"detail":"Invalid Google token"},status=400)
        
        google_id = payload["sub"]
        email = payload["email"]
        
        
        user = User.objects.filter(google_id=google_id).first()
        
        if not user:
            user = User.objects.filter(email=email).first()
            if user:
                user.google_id = google_id
                user.is_verified = True
                user.save()
            else:
                user = User.objects.create(
                    email=email,
                    google_id=google_id,
                )
        
                user.set_unusable_password()
                user.save()
        
        has_profile = ClientProfile.objects.filter(user_id=user.id).exists()
        
        refresh = RefreshToken.for_user(user)
        
        resp = Response(
            {
                "user":{
                    "email":user.email,
                    "role":user.role,
                    "has_profile":has_profile,
                }
            },
            status=status.HTTP_200_OK
        )
        
        set_jwt_cookies(resp,refresh)
        return resp
        
        
        