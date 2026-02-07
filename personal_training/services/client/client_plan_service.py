import logging
from datetime import timedelta
from django.db import transaction, DatabaseError, IntegrityError
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from personal_training.models import TrainingPlan, ClientPlan
from ...constant.client_plans import (
    FIXED_SESSIONS_PER_WEEK,
    FIXED_SESSION_DURATION_MINUTES
)

logger = logging.getLogger(__name__)

"""
receive plan id as input and create the selected plan for the client. 
"""

class ClientPlanService:

    @staticmethod
    def _get_plan(plan_id):
        try:
            return TrainingPlan.objects.get(
                id=plan_id,
                is_active=True
            )
        except TrainingPlan.DoesNotExist:
            raise ValidationError("Selected plan is not available.")

    @staticmethod
    def _deactivate_existing_plans(client):
        ClientPlan.objects.filter(
            client=client,
            is_active=True
        ).update(is_active=False)

    
    @staticmethod
    @transaction.atomic
    def create_plan(client, plan_id, start_date=None):
        try:
            if not client:
                raise ValidationError("Client is required.")

            if not start_date:
                start_date = now().date()

            plan = ClientPlanService._get_plan(plan_id)
            
            end_date = start_date + timedelta(days=plan.duration_days)


            ClientPlanService._deactivate_existing_plans(client)

            client_plan = ClientPlan.objects.create(
                client=client,
                plan=plan,
                start_date=start_date,
                end_date=end_date,
                sessions_per_week=FIXED_SESSIONS_PER_WEEK,
                session_duration_minutes=FIXED_SESSION_DURATION_MINUTES,
                is_active=True
            )

            return client_plan 

        except ValidationError:
            raise

        except IntegrityError as e:
            logger.exception("Integrity error while creating client plan")
            raise ValidationError(
                "Plan could not be created due to a data conflict."
            ) from e

        except DatabaseError as e:
            logger.exception("Database error while creating client plan")
            raise ValidationError(
                "Server error while creating plan. Please try again later."
            ) from e

        except Exception as e:
            logger.exception("Unexpected error while creating client plan")
            raise ValidationError(
                "Unexpected error occurred while creating plan."
            ) from e
