from django.urls import path
from .views import ClientSignupView,TrainerSignupView,VerifySignupView,LoginView,RefreshView,MeView,GetCsrfToken,LogoutView
from .views import ForgotPasswordView,VerifyResetOTPView,ResetPasswordView,ResendResetOTPView,GoogleAuthView

urlpatterns = [
   path("client_signup/", ClientSignupView.as_view()),
   path("trainer_signup/", TrainerSignupView.as_view()),
   path('verify-otp/',VerifySignupView.as_view()),
   path('login/',LoginView.as_view()),
   path('refresh/',RefreshView.as_view()),
   path("me/",MeView.as_view()),
   path("csrf/",GetCsrfToken.as_view()),
   path("logout/",LogoutView.as_view()),
   path("forgot-password/",ForgotPasswordView.as_view()),
   path("verify-reset-otp/",VerifyResetOTPView.as_view()),
   path("reset-password/",ResetPasswordView.as_view()),
   path("resend-otp/",ResendResetOTPView.as_view()),
   path("google-auth",GoogleAuthView.as_view())

]
