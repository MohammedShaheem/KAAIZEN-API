import json
from django.conf import settings

redis_client = settings.REDIS_CLIENT

BOOKING_KEY = "client_booking:{}"
BOOKING_EXPIRY = 60 * 30  # 30 minutes


def _get_key(client_id):
    return BOOKING_KEY.format(client_id)


def save_booking_field(client_id, field, value):
   
    key = _get_key(client_id)

    data = redis_client.get(key)

    if data:
        data = json.loads(data)
    else:
        data = {}

    data[field] = value

    redis_client.set(
        key,
        json.dumps(data),
        ex=BOOKING_EXPIRY
    )

    return True


def get_booking_data(client_id):
    key = _get_key(client_id)
    data = redis_client.get(key)

    return json.loads(data) if data else None


def delete_booking_data(client_id):
    redis_client.delete(_get_key(client_id))
