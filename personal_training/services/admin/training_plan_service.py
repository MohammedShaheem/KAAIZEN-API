from django.db.models import Count, Q
from django.utils.timezone import now
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError, DatabaseError
import logging

from personal_training.models import TrainingPlan

logger = logging.getLogger(__name__)



class TrainingPlanService:
    @staticmethod
    @transaction.atomic
    def create_plan(
        name,
        duration_days,
        price,
        description,
        is_active):

        try:
            if not name or not name.strip():
                raise ValidationError("Plan name is required.")

            if not isinstance(duration_days, int) or duration_days <= 0:
                raise ValidationError("Duration must be a positive number of days.")

            if price is None or float(price) <= 0:
                raise ValidationError("Price must be greater than zero.")

            if TrainingPlan.objects.filter(name__iexact=name.strip()).exists():
                raise ValidationError("A plan with this name already exists.")

            plan = TrainingPlan.objects.create(
                name=name.strip(),
                duration_days=duration_days,
                price=price,
                description=description.strip(),
                is_active=is_active
            )

            logger.info(
                "Training plan created | id=%s | name=%s | duration=%s | price=%s",
                plan.id,
                plan.name,
                plan.duration_days,
                plan.price
            )

            return plan

        except ValidationError:
            raise

        except IntegrityError as e:
            logger.exception("Integrity error while creating training plan")
            raise ValidationError(
                "A plan with similar details already exists."
            ) from e

        except DatabaseError as e:
            logger.exception("Database error while creating training plan")
            raise ValidationError(
                "Server error while creating plan. Please try again later."
            ) from e

        except Exception as e:
            logger.exception("Unexpected error while creating training plan")
            raise ValidationError(
                "Unexpected error occurred while creating plan."
            ) from e
    
    @staticmethod
    def list_plans_with_usage():
        logger.info(f"entering here from list plan with usage")
        return TrainingPlan.objects.annotate(
            active_subscriptions=Count(
                "subscriptions",
                filter=Q(subscriptions__is_active=True)

            )
        )

