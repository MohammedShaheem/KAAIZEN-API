from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

from trainers.models import TrainerProfile, TrainerLeave
from personal_training.models import TrainingSession
from personal_training.choices import TrainingSessionStatus
from trainers.choices import Status

import logging
logger = logging.getLogger(__name__)


class TrainerReassignmentService:

    @staticmethod 
    def _get_session_datetime(session):
        return timezone.make_aware(
            datetime.combine(session.session_date, session.start_time)
        )

    @staticmethod
    def _find_replacement_trainer(session, excluded_trainer):
        required_skills = excluded_trainer.skills
        #finding trainers with same skills
        candidates = TrainerProfile.objects.filter(
            is_active=True,
            is_verified=True,
            skills__contains=required_skills,
        ).exclude(id=excluded_trainer.id)
        #finding any session time conflict with the trainers founded
        for trainer in candidates:
            conflict = TrainingSession.objects.filter(
                trainer=trainer,
                session_date=session.session_date,
                start_time__lt=session.end_time,
                end_time__gt=session.start_time,
                status=TrainingSessionStatus.SCHEDULED,
            ).exists()

            if not conflict:
                return trainer

        return None

    @staticmethod
    @transaction.atomic
    def process_leave_reassignment(leave: TrainerLeave):
        if leave.leave_status != Status.PLANNED:
            return
        #taking the the sessions assigned to the trainer, avoiding race condition.
        affected_sessions = TrainingSession.objects.select_for_update().filter(
            trainer=leave.trainer,
            session_date__gte=leave.start_date,
            session_date__lte=leave.end_date,
            status=TrainingSessionStatus.SCHEDULED,
        )

        #for each sessions in the session founded earlier finding the replacement trainers.
        for session in affected_sessions:
            replacement = TrainerReassignmentService._find_replacement_trainer(
                session=session,
                excluded_trainer=leave.trainer,
            )

            if replacement:
                session.trainer = replacement
                session.status = TrainingSessionStatus.REASSIGNED
                session.save(update_fields=["trainer", "status"])
            else:
                session.status = TrainingSessionStatus.CANCELLED_BY_SYSTEM
                session.save(update_fields=["status"])
                # RefundService.create_credit_from_session(session)

        logger.info(
            "Processed reassignment for leave %s (trainer=%s)",
            leave.id,
            leave.trainer.id
        )
