from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import transaction, DatabaseError, IntegrityError
from django.utils.timezone import now
from datetime import date
import logging

logger = logging.getLogger(__name__)

from ..choices import Status
from trainers.models import TrainerLeave
from trainers.services.trainer_leave_reassignment_service import TrainerReassignmentService

class TrainerLeaveService:
    MAX_LEAVES_PER_MONTH = 2
    """
    for finding start and end of the month
    """
    @staticmethod
    def _get_month_range(target_date: date):
        try:
            start = target_date.replace(day=1)
            if target_date.month == 12:
                end = target_date.replace(
                    year=target_date.year + 1,
                    month=1,
                    day=1
                )
            else:
                end = target_date.replace(
                    month=target_date.month + 1,
                    day=1
                )
            return start, end
        except Exception as e:
            logger.exception("Failed to calculate month range")
            raise ValidationError("Invalid date provided.") from e
    
    
    @staticmethod
    def validate_leave_limit(trainer, start_date):
        if not trainer:
            raise ValidationError("Trainer is required.")

        if not isinstance(start_date, date):
            raise ValidationError("Invalid start date format.")

        try:
            month_start, month_end = TrainerLeaveService._get_month_range(start_date)

            leave_count = TrainerLeave.objects.filter(
                trainer=trainer,
                leave_status=Status.PLANNED,
                start_date__lt=month_end,
                end_date__gte=month_start,
            ).count()


        except DatabaseError as e:
            logger.exception("Database error while checking leave limit")
            raise ValidationError(
                "Could not verify leave limit. Please try again later."
            ) from e

        if leave_count >= TrainerLeaveService.MAX_LEAVES_PER_MONTH:
            raise ValidationError(
                "You can take a maximum of 2 leaves per month."
            )
    @staticmethod
    def validate_overlapping_leave(trainer, start_date, end_date, instance_id=None):
        if not trainer:
            raise ValidationError("Trainer is required.")

        if start_date > end_date:
            raise ValidationError("Start date cannot be after end date.")

        try:
            overlapping = TrainerLeave.objects.filter(
                trainer=trainer,
                start_date__lte=end_date,
                end_date__gte=start_date,
            )

            if instance_id:
                overlapping = overlapping.exclude(id=instance_id)

        except DatabaseError as e:
            logger.exception("Database error while checking overlapping leave")
            raise ValidationError(
                "Could not validate overlapping leave. Please try again later."
            ) from e

        if overlapping.exists():
            raise ValidationError(
                "This leave overlaps with an existing leave."
            )


    @staticmethod
    @transaction.atomic
    def create_leave(trainer, start_date, end_date, reason=""):
        try:
            if not trainer:
                raise ValidationError("Trainer is required.")

            if not isinstance(start_date, date) or not isinstance(end_date, date):
                raise ValidationError("Invalid date format.")

            if start_date > end_date:
                raise ValidationError(
                    "End date cannot be earlier than start date."
                )

            TrainerLeaveService.validate_leave_limit(
                trainer=trainer,
                start_date=start_date
            )

            TrainerLeaveService.validate_overlapping_leave(
                trainer=trainer,
                start_date=start_date,
                end_date=end_date
            )

            leave = TrainerLeave.objects.create(
            trainer=trainer,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            leave_status=Status.PLANNED,
            created_by=trainer.user,
        )
        #reassignment only works after commit, on_commit only takes a funtion with 0 arguments
            transaction.on_commit(
            lambda: TrainerReassignmentService.process_leave_reassignment(leave)
        )
            return leave

        except ValidationError:
            raise

        except IntegrityError as e:
            logger.exception("Integrity error while creating leave")
            raise ValidationError(
                "Leave could not be created due to a data conflict."
            ) from e

        except DatabaseError as e:
            logger.exception("Database error while creating leave")
            raise ValidationError(
                "A server error occurred while creating leave. Please try again later."
            ) from e

        except Exception as e:
            logger.exception("Unexpected error while creating leave")
            raise ValidationError(
                "An unexpected error occurred. Please contact support."
            ) from e