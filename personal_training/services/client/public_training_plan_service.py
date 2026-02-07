import logging
from personal_training.models import TrainingPlan

logger = logging.getLogger(__name__)


class PublicTrainingPlanService:

    @staticmethod
    def list_active_plans():
        logger.info("Fetching active public training plans")

        return TrainingPlan.objects.filter(
            is_active=True
        ).order_by("price")
