import logging
from django.core.exceptions import ValidationError
from personal_training.models import TrainingPlan

logger = logging.getLogger(__name__)


class PublicTrainingPlanDetailService:
    @staticmethod
    def get_active_plan(plan_id):
        try:
            logger.info("Fetching public training plan detail | id=%s", plan_id)

            return TrainingPlan.objects.get(
                id=plan_id,
                is_active=True  
            )

        except TrainingPlan.DoesNotExist:
            logger.warning(
                "Public training plan not found or inactive | id=%s",
                plan_id
            )
            raise ValidationError("Training plan not found.")
