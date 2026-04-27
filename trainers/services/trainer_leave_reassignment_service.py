from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from django.db.models import Exists,OuterRef

from trainers.models import TrainerProfile, TrainerLeave
from personal_training.models import TrainingSession
from personal_training.choices import TrainingSessionStatus
from trainers.choices import Status
from wallet.services.refund.session_refund_service import SessionRefundService,RefundServiceError

import logging
logger = logging.getLogger(__name__)


class TrainerReassignmentService:

    @staticmethod 
    def _get_session_datetime(session):
        return timezone.make_aware(
            datetime.combine(session.session_date, session.start_time)
        )
    #using corelated subquery for checking the available trainers(outerref,exists)
    #fetch all trainers annotate each with has conflict
    #filtering only those who dont have conflict
    
    @staticmethod
    def _find_replacement_trainer(session, excluded_trainer):
        required_skills = excluded_trainer.skills

        conflict_subquery = TrainingSession.objects.filter(
            trainer_id=OuterRef('pk'),          
            session_date=session.session_date,
            start_time__lt=session.end_time,
            end_time__gt=session.start_time,
            status=TrainingSessionStatus.SCHEDULED,
        )

        replacement = TrainerProfile.objects.filter(
            is_active=True,
            is_verified=True,
            skills__contains=required_skills,
        ).exclude(
            id=excluded_trainer.id
        ).annotate(
            has_conflict=Exists(conflict_subquery)   
        ).filter(
            has_conflict=False                        
        ).first()                                    

        return replacement  

    @staticmethod
    @transaction.atomic
    def process_leave_reassignment(leave: TrainerLeave):
        logger.info("entering here from process leave reassignment service")
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
            #if replacement found replacing otherwise cancelling session
            if replacement:
                session.trainer = replacement
                session.status = TrainingSessionStatus.REASSIGNED
                session.save(update_fields=["trainer", "status"])
            else:
                session.status = TrainingSessionStatus.CANCELLED_BY_SYSTEM
                session.save(update_fields=["status"])
                try:
                    SessionRefundService.process_session_refund(session,"system_no_trainer")
                    
                except RefundServiceError as e:
                    
                    logger.error(
                        "Refund failed for session %s: %s",
                        session.id, str(e)
                    )

        logger.info(
            "Processed reassignment for leave %s (trainer=%s)",
            leave.id,
            leave.trainer.id
        )
