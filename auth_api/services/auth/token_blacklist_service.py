from django.conf import settings



def blacklist_refresh_token(refresh_token):
    try:
        jti = refresh_token.get_jti()
        expiry = refresh_token.lifetime
        key = f"blacklist:{jti}"
        settings.REDIS_CLIENT.setex(key, expiry.total_seconds(),"true")
        return True
    except Exception:
        return False