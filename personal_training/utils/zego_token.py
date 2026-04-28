import base64, json, os, random, struct, time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import logging
logger = logging.getLogger(__name__)


def generate_zego_token04(
    app_id: int,
    user_id: str,
    server_secret: str,
    effective_time: int = 3600,
    room_id: str = "",
) -> str:
    nonce = random.randint(-(1 << 31), (1 << 31) - 1)
    now = int(time.time())
    expire = now + effective_time

    privilege_payload = json.dumps({
        "room_id": room_id,
        "privilege": {"1": 1, "2": 1},
        "stream_id_list": []
    }, separators=(",", ":"))

    body = json.dumps({
        "app_id": app_id,
        "user_id": user_id,
        "nonce": nonce,
        "ctime": now,
        "expire": expire,
        "payload": privilege_payload,
    }, separators=(",", ":"))

    key = server_secret.encode("utf-8")
    iv = bytes(16)     

    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(body.encode("utf-8"), AES.block_size))

    buf  = struct.pack(">H", 4)
    buf += struct.pack(">I", expire)
    buf += struct.pack(">H", len(iv)) + iv
    buf += struct.pack(">H", len(ciphertext)) + ciphertext
    
    print(f"Generated Zego token for user:{user_id} room:{room_id}")
    
    return "04" + base64.b64encode(buf).decode("utf-8")