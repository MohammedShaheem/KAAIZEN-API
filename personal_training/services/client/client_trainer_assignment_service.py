import logging
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.utils.timezone import now

from personal_training.models import ClientTrainerAssignment, TrainingSession
from trainers.models import TrainerProfile
from clients.models import ClientProfile
from personal_training.constant.scheduling import SESSIONS_PER_CYCLE

logger = logging.getLogger(__name__)


class ClientTrainerAssignmentService:

    @staticmethod
    def get_available_trainers(start_time, end_time, client_id):
    
    
            client = ClientProfile.objects.only("preferred_workout_type").get(
                user_id=client_id
            )
            preferred_workout = [client.preferred_workout_type]
           

            
            busy_trainers = TrainingSession.objects.filter(
                start_time__lt=end_time,
                end_time__gt=start_time,
                status="scheduled"
            ).values_list("trainer_id", flat=True) 
            logger.info(f'busy trainers:',busy_trainers) 
            available_trainers = TrainerProfile.objects.filter(
                skills__contains=preferred_workout, 
                is_active=True,
                is_verified=True,
            ).exclude(
                id__in=busy_trainers
            )
            logger.info(f'available trainer:',available_trainers)

            return available_trainers
        

    @staticmethod
    def assign_trainer_and_create_sessions(
        client,
        trainer,
        preferred_start_time,
        preferred_end_time
    ):
        logger.info("ASSIGNMENT: creating assignment")

        if preferred_start_time >= preferred_end_time:
            raise ValidationError("Start time must be before end time.")

        try:
            ClientTrainerAssignment.objects.filter(
                client=client,
                is_active=True
            ).update(is_active=False)

            assignment = ClientTrainerAssignment.objects.create(
                client=client,
                trainer=trainer,
                preferred_start_time=preferred_start_time,
                preferred_end_time=preferred_end_time,
                is_active=True
            )

            logger.info("ASSIGNMENT: creating sessions")

            try:
                ClientTrainerAssignmentService._create_session_cycle(
                    client,
                    trainer,
                    preferred_start_time,
                    preferred_end_time
                )
            except Exception:
                logger.exception(
                    "Session creation failed; assignment kept active"
                )

            logger.info("ASSIGNMENT: finished")
            return assignment

        except DatabaseError as e:
            logger.exception("Database error while assigning trainer")
            raise ValidationError("Failed to assign trainer.") from e

    @staticmethod
    def _create_session_cycle(client, trainer, start_time, end_time):
        today = now().date()
        sessions = []

        for i in range(SESSIONS_PER_CYCLE):
            session_date = today + timedelta(days=i)
            sessions.append(
                TrainingSession(
                    client=client,
                    trainer=trainer,
                    session_date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                    created_by_system=True
                )
            )

        TrainingSession.objects.bulk_create(sessions)
