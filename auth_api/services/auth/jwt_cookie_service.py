from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response



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