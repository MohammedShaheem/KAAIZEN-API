import logging
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from trainers.models import TrainerProfile
from personal_training.utils.client_booking_cache import (
    get_booking_data,
    delete_booking_data
)
from personal_training.services.client.client_trainer_assignment_service import (
    ClientTrainerAssignmentService
)
from personal_training.models import ClientTrainerAssignment
from clients.models import ClientProfile
from datetime import time

redis_client = settings.REDIS_CLIENT
logger = logging.getLogger(__name__)


import logging
from datetime import time
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from trainers.models import TrainerProfile
from clients.models import ClientProfile
from personal_training.utils.client_booking_cache import (
    get_booking_data,
    delete_booking_data
)
from personal_training.services.client.client_trainer_assignment_service import (
    ClientTrainerAssignmentService
)

redis_client = settings.REDIS_CLIENT
logger = logging.getLogger(__name__)


class ConfirmAssignmentService:

    @staticmethod
    @transaction.atomic
    def confirm(client):
        client_profile = ClientProfile.objects.get(user=client)

        existing = ClientTrainerAssignment.objects.filter(
            client=client_profile,
            is_active=True
        ).first()

        if existing:
            logger.info("Confirm called again – returning existing assignment")
            return existing

        booking = get_booking_data(client.id)
        if not booking:
            raise ValidationError("Booking session expired.")

        trainer_id = booking.get("trainer_id")
        start_time_raw = booking.get("start_time")
        end_time_raw = booking.get("end_time")

        if not trainer_id or not start_time_raw or not end_time_raw:
            raise ValidationError("Incomplete booking data.")

        lock_key = f"trainer_lock:{trainer_id}:{start_time_raw}:{end_time_raw}"
        lock_owner = redis_client.get(lock_key)

        if not lock_owner or str(lock_owner) != str(client.id):
            raise ValidationError("Trainer reservation expired.")

        start_time = time.fromisoformat(start_time_raw)
        end_time = time.fromisoformat(end_time_raw)

        trainer = TrainerProfile.objects.get(id=trainer_id)

        assignment = ClientTrainerAssignmentService.assign_trainer_and_create_sessions(
            client=client_profile,
            trainer=trainer,
            preferred_start_time=start_time,
            preferred_end_time=end_time
        )

        try:
            redis_client.delete(lock_key)
            delete_booking_data(client.id)
        except Exception:
            logger.warning(
                "Redis cleanup failed after assignment",
                extra={"client_id": str(client.id), "lock_key": lock_key}
            )

        return assignment
