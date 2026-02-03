from django.urls import path
from .views.client_signup_view import ClientSignupView
from .views.trainer_signup_view import TrainerSignupView
from .views.verify_signup_view import VerifySignupView
from .views.login_view import LoginView
from .views.refresh_view import RefreshView
from .views.me_view import MeView
from .views.csrftoken_view import GetCsrfToken
from .views.logout_view import LogoutView
from .views.forgot_password_view import ForgotPasswordView
from .views.verify_reset_otp_view import VerifyResetOTPView
from .views.reset_password_view import ResetPasswordView
from .views.resend_signup_otp_view import ResendSignupOTPView
from .views.otp_management_view import ResendResetOTPView
from .views.google_auth_view import GoogleAuthView



urlpatterns = [
   path("client_signup/", ClientSignupView.as_view()),
   path("trainer_signup/", TrainerSignupView.as_view()),
   path('verify-otp/',VerifySignupView.as_view()),
   path("signup/resend-otp/", ResendSignupOTPView.as_view()),
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
