import logging
from django.conf import settings
from django.core.exceptions import ValidationError

from personal_training.utils.client_booking_cache import (
    get_booking_data,
    save_booking_field
)

redis_client = settings.REDIS_CLIENT
logger = logging.getLogger(__name__)

LOCK_EXPIRY = 60 * 5  # 5 minutes


class TrainerSelectionService:

    @staticmethod
    def select_trainer_and_lock_slot(client_id, trainer_id):

        try:
            booking = get_booking_data(client_id)

            if not booking:
                raise ValidationError("Booking session expired.")

            start_time = booking.get("start_time")
            end_time = booking.get("end_time")

            if not start_time or not end_time:
                raise ValidationError("Please select slot first.")

            lock_key = f"trainer_lock:{trainer_id}:{start_time}:{end_time}"


            
            locked = redis_client.set(
                lock_key,
                str(client_id),
                nx=True,
                ex=LOCK_EXPIRY
            )

            if not locked:
                raise ValidationError(
                    "Trainer is temporarily reserved by another client. Please choose another trainer."
                )

            
            save_booking_field(client_id, "trainer_id", str(trainer_id))

            return True

        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Trainer selection failed")
            raise ValidationError(
                "Unable to reserve trainer at this time."
            ) from e
