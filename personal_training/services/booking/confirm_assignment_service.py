from datetime import time
import logging
from datetime import time,date,timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from personal_training.models import ClientTrainerAssignment,ClientPlan
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
    """
    1. checking for the client already assigned.
    2. from the redis getting the booking data.
    3. fetching trainer.
    """
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

        client_plan = ClientPlan.objects.filter(
            client=client_profile,
            status="paid",
            is_active=False
        ).order_by("-created_at").first()

        if not client_plan:
            raise ValidationError("No paid plan found.")
        
        trainer_id = booking.get("trainer_id")
        start_time_raw = booking.get("start_time")
        logger.info(f"start time form confirm assignment{start_time_raw}")
        end_time_raw = booking.get("end_time")
        start_date = booking.get("start_date")
        logger.info(f"end time form confirm assignment{end_time_raw}")

        if not trainer_id or not start_time_raw or not end_time_raw:
            raise ValidationError("Incomplete booking data.")

        lock_key = f"trainer_lock:{trainer_id}:{start_time_raw}:{end_time_raw}"
        lock_owner = redis_client.get(lock_key)

        if not lock_owner or str(lock_owner) != str(client.id):
            raise ValidationError("Trainer reservation expired.")

        start_time = time.fromisoformat(start_time_raw)
        end_time = time.fromisoformat(end_time_raw)

        trainer = TrainerProfile.objects.get(id=trainer_id)
        
        start_date_obj = date.fromisoformat(start_date)

        end_date = start_date_obj + timedelta(
            days=client_plan.plan.duration_days
        )
        client_plan.start_date = start_date_obj
        client_plan.end_date = end_date
        client_plan.status = "active"
        client_plan.is_active = True
        client_plan.save()

        assignment = ClientTrainerAssignmentService.assign_trainer_and_create_sessions(
            client=client_profile,
            trainer=trainer,
            client_plan = client_plan,
            preferred_start_time=start_time,
            preferred_end_time=end_time,
            start_date = start_date,
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
