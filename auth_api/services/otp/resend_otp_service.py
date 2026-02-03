import random
from django.conf import settings
from django.core.mail import send_mail


redis_client = settings.REDIS_CLIENT
RESET_OTP_EXPIRY = 300

def generate_otp():
    return str(random.randint(100000,999999))
    





RESET_RESEND_COOLDOWN = 30
MAX_RESENDS_PER_HOUR = 10

def resend_reset_otp(email):
    otp_key = f"reset_otp:{email}"
    resend_key = f"reset_resend:{email}"
    
    # cooldown check
    if redis_client.get(resend_key):
        raise Exception("Please wait before requesting OTP again.")
    
    #per hour rate limiting
    resend_count_key = f"reset_resend_count:{email}"
    resend_count = redis_client.get(resend_count_key)
    resend_count = int(resend_count) if resend_count else 0 
    
    if resend_count >= MAX_RESENDS_PER_HOUR:
        raise Exception("Too many resend requests. Try again in 1 hour.")
    
    redis_client.delete(otp_key)
    
    otp = generate_otp()
    redis_client.setex(otp_key,RESET_OTP_EXPIRY,otp)
    
    redis_client.incr(resend_count_key)
    redis_client.expire(resend_count_key,3600)
    
    redis_client.setex(resend_key,RESET_RESEND_COOLDOWN,1)
    
    send_mail(
        "Password Reset OTP",
        f"Your password reset OTP is {otp}. It expires in 5 minutes.",
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    
    return True

