import logging
from datetime import time, timedelta, datetime
from django.core.exceptions import ValidationError

from personal_training.utils.client_booking_cache import save_booking_field

logger = logging.getLogger(__name__)

MORNING_RANGE = (time(5, 0), time(10, 0))
EVENING_RANGE = (time(16, 0), time(21, 0))


class SlotService:

    @staticmethod
    def generate_and_store_slots(client_id, session_type):
        """
        Stores selected session_type in redis
        and returns generated slots
        """

        try:
            if session_type not in ["morning", "evening"]:
                raise ValidationError("Invalid session type selected.")

            
            save_booking_field(client_id, "session_type", session_type)

            if session_type == "morning":
                start, end = MORNING_RANGE
            else:
                start, end = EVENING_RANGE

            slots = []

            current = datetime.combine(datetime.today(), start)
            end_dt = datetime.combine(datetime.today(), end)

            while current < end_dt:
                slot_end = current + timedelta(hours=1)

                slots.append({
                    "start_time": current.strftime("%H:%M"),
                    "end_time": slot_end.strftime("%H:%M")
                })

                current = slot_end

            return slots

        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Slot generation failed")
            raise ValidationError(
                "Unable to generate session slots. Please try again."
            ) from e
