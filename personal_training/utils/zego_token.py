import base64, json, random, struct, time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def generate_zego_token04(
    app_id: int,
    user_id: str,
    server_secret: str,
    effective_time: int = 3600,
    payload: str = ""
) -> str:
    nonce = random.randint(-(1 << 31), (1 << 31) - 1)
    now = int(time.time())
    expire = now + effective_time

    body = json.dumps({
        "app_id": app_id,
        "user_id": user_id,
        "nonce": nonce,
        "ctime": now,
        "expire": expire,
        "payload": payload,
    }, separators=(",", ":"))

    # server_secret is 32 hex chars = 16 bytes AES-128 key
    key = bytes.fromhex(server_secret)
    iv  = struct.pack(">II", now, expire) + b"\x00" * 8 

    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(body.encode("utf-8"), AES.block_size))

    buf  = struct.pack(">H", 4)                             
    buf += struct.pack(">I", expire)                         
    buf += struct.pack(">H", len(iv)) + iv                   
    buf += struct.pack(">H", len(ciphertext)) + ciphertext   

    return "04" + base64.b64encode(buf).decode("utf-8")