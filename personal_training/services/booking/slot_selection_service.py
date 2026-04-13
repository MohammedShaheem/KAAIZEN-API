import logging
from django.core.exceptions import ValidationError

from personal_training.utils.client_booking_cache import save_booking_field
from personal_training.services.client.client_trainer_assignment_service import (
    ClientTrainerAssignmentService
)
from personal_training.utils.client_booking_cache import (
    get_booking_data
)

logger = logging.getLogger(__name__)


class SlotSelectionService:
    @staticmethod
    def select_slot_and_fetch_trainers(client_id, start_time, end_time):
        try:
            logger.info(f'client id:',client_id)
            save_booking_field(client_id, "start_time", str(start_time))
            save_booking_field(client_id, "end_time", str(end_time))
            booking_data = get_booking_data(client_id)
            session_type = booking_data.get("session_type")
           
            trainers = ClientTrainerAssignmentService.get_available_trainers(
                start_time,
                end_time,
                client_id,
                session_type
            )

            return trainers

        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Failed to process slot selection")
            raise ValidationError(
                "Unable to fetch available trainers. Try again."
            ) from e
