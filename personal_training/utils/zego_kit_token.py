import hmac
import hashlib
import time
import json
import random
import struct
import zlib
import base64

def generate_kit_token(app_id: int, server_secret: str, room_id: str,
                        user_id: str, user_name: str, expiry_seconds: int = 3600) -> str:
    
    effective_time = expiry_seconds
    create_time = int(time.time())
    expire_time = create_time + effective_time
    nonce = random.randint(-2147483648, 2147483647)

    
    payload = {
        "room_id": room_id,
        "user_id": user_id,
        "user_name": user_name,
        "privilege": {
            "1": 1,  
            "2": 1,  
        },
        "stream_id_list": None,
    }

    payload_str = json.dumps(payload, separators=(',', ':'))

    
    content = (
        struct.pack(">I", app_id) +
        struct.pack(">i", create_time) +
        struct.pack(">i", expire_time) +
        struct.pack(">i", nonce) +
        payload_str.encode("utf-8")
    )

    
    mac = hmac.new(server_secret.encode("utf-8"), content, hashlib.sha256).digest()

    
    token_buf = (
        mac +
        struct.pack(">i", create_time) +
        struct.pack(">i", expire_time) +
        struct.pack(">i", nonce) +
        struct.pack(">H", len(payload_str)) +
        payload_str.encode("utf-8")
    )

    
    compressed = zlib.compress(token_buf)
    token = "04" + base64.b64encode(compressed).decode("utf-8")

    return token