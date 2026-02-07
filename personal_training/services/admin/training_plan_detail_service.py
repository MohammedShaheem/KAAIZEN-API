import logging
from django.db import transaction, DatabaseError, IntegrityError
from django.core.exceptions import ValidationError

from personal_training.models import TrainingPlan

logger = logging.getLogger(__name__)


class TrainingPlanDetailService:

    @staticmethod
    def get_plan_with_clients(plan_id):
        try:
            return TrainingPlan.objects.prefetch_related(
                "subscriptions__client__user"
            ).get(id=plan_id)

        except TrainingPlan.DoesNotExist:
            raise ValidationError("Training plan not found.")

    @staticmethod
    @transaction.atomic
    def set_plan_active_status(plan_id, is_active: bool):
        try:
            plan = TrainingPlan.objects.select_for_update().get(id=plan_id)

            if plan.is_active == is_active:
                return plan

            plan.is_active = is_active
            plan.save(update_fields=["is_active"])

            logger.info(
                "Plan status changed | id=%s | is_active=%s",
                plan.id,
                is_active
            )

            return plan

        except TrainingPlan.DoesNotExist:
            raise ValidationError("Training plan not found.")

        except IntegrityError as e:
            logger.exception("Integrity error while updating plan status")
            raise ValidationError("Could not update plan status.") from e

        except DatabaseError as e:
            logger.exception("Database error while updating plan status")
            raise ValidationError("Server error while updating plan status.") from e
