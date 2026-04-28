import time

import logging
from typing import Dict
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from personal_training.utils.zego_token import generate_zego_token04

logger = logging.getLogger(__name__)


class ZegoTokenService:
    DEFAULT_EXPIRY_SECONDS = 3600

    @staticmethod
    def generate(user_id, room_id, expiry_seconds, username):
        try:
            if not user_id or not isinstance(user_id, str):
                raise ValueError("Invalid user_id provided")
            if not room_id or not isinstance(room_id, str):
                raise ValueError("Invalid room_id provided")

            if not getattr(settings, "ZEGO_APP_ID", None):
                raise ImproperlyConfigured("ZEGO_APP_ID is not configured")
            if not getattr(settings, "ZEGO_SERVER_SECRET", None):
                raise ImproperlyConfigured("ZEGO_SERVER_SECRET is not configured")

            try:
                app_id = int(settings.ZEGO_APP_ID)
            except (TypeError, ValueError):
                raise ImproperlyConfigured("ZEGO_APP_ID must be a valid integer")

            expiry = expiry_seconds or ZegoTokenService.DEFAULT_EXPIRY_SECONDS
            expire_time = int(time.time()) + expiry

            token = generate_zego_token04(
                app_id=app_id,
                user_id=user_id,
                server_secret=settings.ZEGO_SERVER_SECRET,
                effective_time=expiry,
                room_id=room_id,  
            )

            return {
                "appID": app_id,
                "token": token,
                "userID": user_id,
                "roomID": room_id,
                "expiresAt": expire_time,
            }

        except Exception:
            logger.exception(
                "Failed to generate Zego token",
                extra={"user_id": user_id, "room_id": room_id},
            )
            raise RuntimeError("Token generation failed")