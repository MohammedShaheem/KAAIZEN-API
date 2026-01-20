import random
from django.conf import settings
from django.core.mail import send_mail


redis_client = settings.REDIS_CLIENT

otp_expiry = 300
max_resends_per_hour = 10
temp_user_expiry = 300


def store_temp_signup_data(email,password,role):
    key = f"temp_user:{email}"
    value = {
        "email":email,
        "password":password,
        "role":role,
    }
    redis_client.hset(key, mapping=value)
    redis_client.expire(key,temp_user_expiry)
    return True

def get_temp_signup_data(email):
    key = f"temp_user:{email}"
    data = redis_client.hgetall(key)
    return data if data else None

def delete_temp_signup_data(email):
    redis_client.delete(f"temp_user:{email}")
    
##########################################################
####################### OTP for User SIGNUP #############

def generate_otp():
    return str(random.randint(100000,999999))

def send_singup_otp(email):
     # for rate limiting per hour
    resend_key = f"otp_resend:{email}"
    resend_count = redis_client.get(resend_key)
    
   
    if resend_count and int(resend_count) >= max_resends_per_hour:
        raise Exception("Too many OTP requests.Try again in 1 hour.")
    
    otp = generate_otp()
    otp_key = f"otp:{email}"
    
    redis_client.setex(otp_key,otp_expiry,otp)
    
    redis_client.incr(resend_key)
    redis_client.expire(resend_key,3600)
    
    send_mail(
        "Your Signup OTP",
        f"Your OTP is {otp}. It expires in 5 minutes.",
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    
    return True

def veriy_signup_otp(email,code):
    otp_key = f"otp:{email}"
    stored_otp = redis_client.get(otp_key)
    
    #expired or never generated
    if not stored_otp:
        return False
    
    #if otp is wrong
    if stored_otp != code:
        return False
    
    #if otp is correct deleting otp from redis
    redis_client.delete(otp_key)
    return True

##############################################################
####################### OTP for Reset Password #############
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
    
    
    
#######################################################################
##################### RESEND OTP for reset Password ####################
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