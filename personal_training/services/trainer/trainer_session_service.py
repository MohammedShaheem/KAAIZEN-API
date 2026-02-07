from django.core.exceptions import ValidationError
from django.utils.timezone import now
from personal_training.models import TrainingSession
from trainers.models import TrainerProfile


class TrainerSessionService:

    @staticmethod
    def get_trainer_sessions(user):
        try:
            trainer = TrainerProfile.objects.get(user=user)
        except TrainerProfile.DoesNotExist:
            raise ValidationError("Trainer profile not found.")

        sessions = (
            TrainingSession.objects
            .filter(trainer=trainer)
            .select_related("client")
            .order_by("session_date", "start_time")
        )

        today = now().date()

        upcoming_session = (
                    sessions
                    .filter(session_date__gte=today)
                    .first()
                )
        past_sessions = sessions.filter(session_date__lt=today)

        return {
            "recent_sessions": [upcoming_session] if upcoming_session else [],
            "all_sessions": sessions,
            "past_sessions": past_sessions,
        }

    @staticmethod
    def get_session_detail(user, session_id):
        try:
            trainer = TrainerProfile.objects.get(user=user)
        except TrainerProfile.DoesNotExist:
            raise ValidationError("Trainer profile not found.")

        try:
            session = TrainingSession.objects.select_related(
                "client", "trainer"
            ).get(id=session_id, trainer=trainer)
        except TrainingSession.DoesNotExist:
            raise ValidationError("Session not found.")

        return session
