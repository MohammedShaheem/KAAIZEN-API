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

################################################################

def generate_otp():
    return str(random.randint(100000,999999))

def send_signup_otp(email):
     # for rate limiting per hour
    resend_key = f"otp_resend:{email}"
    resend_count = redis_client.get(resend_key)
    
    if resend_count and int(resend_count) >= max_resends_per_hour:
        raise Exception("Too many OTP requests. Try again in 1 hour.")
    
    otp = generate_otp()
    otp_key = f"otp:{email}"
    
    redis_client.setex(otp_key, otp_expiry, otp)
    
    redis_client.incr(resend_key)
    redis_client.expire(resend_key, 3600)
    
    email_body = f"""
Hello,

Welcome! We received a request to create an account using this email address.

Please use the verification code below to complete your signup:

Your One-Time Password (OTP):
{otp}

This code is valid for 5 minutes. For your security, please do not share this code with anyone.

If you did not request this signup, you can safely ignore this email.

Best regards,  
Support Team  
Your App Name
"""

    send_mail(
        "Your Signup OTP",
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    
    return True

def verify_signup_otp(email, code):
    otp_key = f"otp:{email}"
    stored_otp = redis_client.get(otp_key)
    print(type(stored_otp), stored_otp)
    print(type(code),code)

    if not stored_otp:
        return False

    if isinstance(stored_otp, bytes):
        stored_otp = stored_otp.decode()

    if stored_otp != code:
        return False

    redis_client.delete(otp_key)
    redis_client.delete(f"otp_resend:{email}")

    return True


def resend_signup_otp(email: str):
    resend_key = f"otp_resend:{email}"
    resend_count = redis_client.get(resend_key)

    if resend_count and int(resend_count) >= max_resends_per_hour:
        raise Exception("Too many OTP requests. Try again in 1 hour.")

    #check if signup is actually pending
    temp_key = f"temp_user:{email}"
    temp_data = redis_client.hgetall(temp_key)


    if not temp_data:
        raise Exception("Signup session expired. Please signup again.")

    otp = generate_otp()
    otp_key = f"otp:{email}"

    redis_client.setex(otp_key, otp_expiry, otp)

    redis_client.incr(resend_key)
    redis_client.expire(resend_key, 3600)
    

    

    email_body = f"""
Hello,

Here is your new verification code for signup:

OTP: {otp}

This code is valid for 5 minutes.

If you did not request this, please ignore this email.

Best regards,
Support Team
"""

    send_mail(
        "Resend Signup OTP",
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )

    return True
