import logging
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.utils.timezone import now
from django.utils import timezone
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import uuid
from django.db.models import Q



from personal_training.models import ClientTrainerAssignment, TrainingSession, ClientPlan
from trainers.models import TrainerProfile
from clients.models import ClientProfile
from trainers.models import TrainerLeave
from trainers.choices import Status
from personal_training.choices import TrainingSessionStatus 
from personal_training.constant.share_percentage import TRAINER_PERCENT,ADMIN_PERCENT

logger = logging.getLogger(__name__)


class ClientTrainerAssignmentService:

    @staticmethod
    def get_available_trainers(start_time, end_time, client_id, session_type):   
            client = ClientProfile.objects.only("preferred_workout_type").get(
                user_id=client_id
            )
            preferred_workout = [client.preferred_workout_type]
            
            busy_trainers = TrainingSession.objects.filter(
                start_time__lt=end_time,
                end_time__gt=start_time,
                status="scheduled"
            ).values_list("trainer_id", flat=True) 
            
            shift_filter = Q(shift_type=session_type) | Q(shift_type="both")
            
            logger.info(f'busy trainers:',busy_trainers) 
            
            available_trainers = TrainerProfile.objects.filter(
                skills__contains=preferred_workout,
                is_active=True,
                is_verified=True,
            ).filter(
                shift_filter
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
        preferred_end_time,
        start_date,
        client_plan,
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
                ClientTrainerAssignmentService.ensure_upcoming_sessions(assignment,start_date,client_plan)
            except Exception:
                logger.exception(
                    "Session creation failed; assignment kept active"
                )

            logger.info("ASSIGNMENT: finished")
            return assignment

        except DatabaseError as e:
            logger.exception("Database error while assigning trainer")
            raise ValidationError("Failed to assign trainer.") from e

    #used for both initial creation and rolling window
    @staticmethod
    def ensure_upcoming_sessions(assignment,start_date, client_plan):
        """
        counting upcoming sessions
        ensure never exceed the total sessions
        getting last existing session date if any
        skiping sunday
        checking whether the trainer is on leave if yes then skipping that day
        checking conflict
        """
        
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        
        today = timezone.now().date()
        
        effective_start = max(today, start_date)


        upcoming_count = TrainingSession.objects.filter(
            client=assignment.client,
            client_plan=client_plan,
            status=TrainingSessionStatus.SCHEDULED,
            session_date__gte=effective_start
        ).count()

        
        total_sessions_created = TrainingSession.objects.filter(
            client=assignment.client,
            client_plan=client_plan
        ).count()
        
        remaining_sessions = client_plan.total_session - total_sessions_created

        if remaining_sessions <= 0:
            return
        
        missing_for_window = max(0, 6 - upcoming_count)

        missing = min(missing_for_window, remaining_sessions)

        
        if missing <= 0:
            return

        sessions_to_create = []
        

        last_session = TrainingSession.objects.filter(
            client=assignment.client,
            client_plan=client_plan
        ).order_by("-session_date").first()
        

        if last_session:
            current_date = last_session.session_date + timedelta(days=1)
        else:
            current_date = effective_start

        created = 0
        
        client_plan = ClientPlan.objects.get(
                client=assignment.client,
                status="active",
                is_active=True
            )
        

        while created < missing:
            if current_date.weekday() == 6:
                current_date += timedelta(days=1)
                continue

            trainer_on_leave = TrainerLeave.objects.filter(
                trainer=assignment.trainer,
                start_date__lte=current_date,
                end_date__gte=current_date,
                leave_status=Status.PLANNED
            ).exists()

            if trainer_on_leave:
                current_date += timedelta(days=1)
                continue

            conflict = TrainingSession.objects.filter(
                trainer=assignment.trainer,
                session_date=current_date,
                start_time__lt=assignment.preferred_end_time,
                end_time__gt=assignment.preferred_start_time,
                status=TrainingSessionStatus.SCHEDULED
            ).exists()

            if conflict:
                current_date += timedelta(days=1)
                continue
            session_price = client_plan.per_session_price
            
            trainer_share = (session_price * TRAINER_PERCENT).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            admin_share = (session_price * ADMIN_PERCENT).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            sessions_to_create.append(
                TrainingSession(
                    client=assignment.client,
                    trainer=assignment.trainer,
                    client_plan=client_plan,
                    session_date=current_date,
                    start_time=assignment.preferred_start_time,
                    end_time=assignment.preferred_end_time,
                    session_price=session_price,
                    trainer_share_amount=trainer_share,
                    admin_share_amount=admin_share,
                    created_by_system=True,
                    status=TrainingSessionStatus.SCHEDULED,
                    room_id=f"session_{uuid.uuid4().hex[:12]}",

                )
            )
            created += 1
            current_date += timedelta(days=1)

        TrainingSession.objects.bulk_create(sessions_to_create)