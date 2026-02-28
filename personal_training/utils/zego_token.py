import time
import json
import base64
import random
import hmac
import hashlib
import gzip
from io import BytesIO


def generate_token04(app_id, server_secret, user_id, room_id, effective_time=3600):

    nonce = random.randint(0, 2147483647)
    ctime = int(time.time())
    expire = ctime + effective_time

    payload = {
        "room_id": room_id,
        "privilege": {
            "1": 1,
            "2": 1
        },
        "stream_id_list": None,
    }

    token_info = {
        "app_id": app_id,
        "user_id": user_id,
        "nonce": nonce,
        "ctime": ctime,
        "expire": expire,
        "payload": payload,
    }

    # signature
    sign_str = json.dumps(token_info, separators=(",", ":"))
    signature = hmac.new(
        server_secret.encode("utf-8"),
        sign_str.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    token_info["signature"] = signature

    # gzip compress
    json_bytes = json.dumps(token_info, separators=(",", ":")).encode("utf-8")

    buf = BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as f:
        f.write(json_bytes)

    compressed = buf.getvalue()

    # token04 format
    return "04" + base64.b64encode(compressed).decode("utf-8")