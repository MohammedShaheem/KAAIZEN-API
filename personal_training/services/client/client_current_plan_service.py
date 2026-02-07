from django.core.exceptions import ValidationError

from clients.models import ClientProfile
from personal_training.models import (
    ClientTrainerAssignment,
    TrainingSession,
    TrainingPlan
)


class ClientCurrentPlanService:

    @staticmethod
    def get_current_plan(user):
        try:
            client = ClientProfile.objects.get(user=user)
        except ClientProfile.DoesNotExist:
            raise ValidationError("Client profile not found.")

        assignment = ClientTrainerAssignment.objects.filter(
            client=client,
            is_active=True
        ).select_related("trainer").first()

        if not assignment:
            raise ValidationError("No active training plan found.")

        plan = (
            TrainingPlan.objects
            .filter(subscriptions__client=client, subscriptions__is_active=True)
            .first()
        )


        sessions = TrainingSession.objects.filter(
            client=client,
            trainer=assignment.trainer
        ).order_by("session_date")

        return {
            "plan": plan,
            "trainer": assignment.trainer,
            "assignment": assignment,
            "sessions": sessions
        }
