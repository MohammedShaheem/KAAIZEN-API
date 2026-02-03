import random
from django.conf import settings
from django.core.mail import send_mail


redis_client = settings.REDIS_CLIENT


def generate_otp():
    return str(random.randint(100000,999999))


RESET_OTP_EXPIRY = 300
RESET_TOKEN_EXPIRY = 600 #10 minutes for setting password after otp verification
MAX_RESET_ATTEMPTS_PER_HOUR = 10

def send_reset_otp(email):
    
    reset_key = f"reset_attempts:{email}"
    attempts = redis_client.get(reset_key)
    attempts = int(attempts) if attempts else 0
    
    if attempts >= MAX_RESET_ATTEMPTS_PER_HOUR:
        raise Exception("Too many reset requests. Try again in 1 hour")
    
    otp = generate_otp()
    otp_key = f"reset_otp:{email}"
    
    
    redis_client.setex(otp_key,RESET_OTP_EXPIRY,otp)
    
    redis_client.incr(reset_key)
    redis_client.expire(reset_key,3600) #reseting count after 1 hour
    
    send_mail(
        "Password Reset OTP",
        f"Your passwrod reset OTP is {otp}. It expires in 5 minutes.",
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    
    return True

def verify_reset_otp(email,otp):
    
    otp_key = f"reset_otp:{email}"
    stored_otp = redis_client.get(otp_key)
    
    if not stored_otp:
        return False
    
    if stored_otp != otp:
        return False
    
    redis_client.delete(otp_key)
    
    reset_token = str(random.randint(100000,999999)) #setting token for autherisation after otp authentication
   
    reset_key = f"reset_token:{email}"
    redis_client.setex(reset_key,RESET_TOKEN_EXPIRY,reset_token)
    
    return reset_token

def verify_reset_token(email,token):
    reset_key = f"reset_token:{email}"
    stored_token = redis_client.get(reset_key)
    
    
    return stored_token == token

def clear_reset_data(email):
    redis_client.delete(f"reset_token:{email}")
    redis_client.delete(f"reset_attempt:{email}")
    