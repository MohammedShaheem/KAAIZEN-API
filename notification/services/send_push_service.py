from firebase_admin import messaging
from notification.models import UserDevice
import logging

logger = logging.getLogger(__name__)

def send_push(user, title, body):
    logger.info(f"Sending push for user {user.id}")

    devices = UserDevice.objects.filter(user=user)
    logger.info(f"Devices count: {devices.count()}")
    for device in devices:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=device.fcm_token,
        )

        messaging.send(message)