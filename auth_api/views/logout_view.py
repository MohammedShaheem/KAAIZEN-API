from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from ..services.auth.token_blacklist_service import blacklist_refresh_token





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