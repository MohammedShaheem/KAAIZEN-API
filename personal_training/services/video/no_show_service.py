import logging
from django.db import transaction
from django.utils import timezone
from personal_training.models import TrainingSession
from personal_training.services.client.session_cancellation_service import SessionCancellationService
from wallet.services.refund.session_refund_service import SessionRefundService

logger = logging.getLogger(__name__)

NO_SHOW_WINDOW_MINUTES = 1


class NoShowCancellationService:

    @staticmethod
    @transaction.atomic
    def check_and_cancel_if_no_show(session_id):
        """
        called by Celery task 10 minutes after either party joins
        checks if the other party never showed up and cancels accordingly
        """
        
        try:
            session = (
                TrainingSession.objects
                .select_for_update()
                .get(id=session_id)
            )
        except TrainingSession.DoesNotExist:
            logger.warning("NoShowService: session %s not found.", session_id)
            return {"skipped": True, "reason": "session_not_found"}
 
        if session.status not in ("scheduled", "in_progress"):
            logger.info(
                "NoShowService: session %s already in status=%s. Skipping.",
                session_id, session.status,
            )
            return {"skipped": True, "reason": f"status_is_{session.status}"}
 
        now = timezone.now()
        trainer_joined = session.trainer_joined_at
        client_joined  = session.client_joined_at
 
        # client did not join
        if trainer_joined and not client_joined:
            elapsed = (now - trainer_joined).total_seconds() / 60
            if elapsed >= NO_SHOW_WINDOW_MINUTES:
                return NoShowCancellationService._cancel_client_no_show(session)
 
        #trainer did not join.
        elif client_joined and not trainer_joined:
            elapsed = (now - client_joined).total_seconds() / 60
            if elapsed >= NO_SHOW_WINDOW_MINUTES:
                return NoShowCancellationService._cancel_trainer_no_show(session)
 
        elif trainer_joined and client_joined:
            return {"skipped": True, "reason": "both_parties_joined"}
 
        else:
            return {"skipped": True, "reason": "neither_party_joined"}
 
        return {"skipped": True, "reason": "window_not_elapsed"}

    

    @staticmethod
    def _cancel_client_no_show(session):
        """
        client didnt joined.
        """
        logger.info(
            "NoShowService: client no-show for session %s. Cancelling without refund.",
            session.id,
        )
        session.status = "cancelled"
        session.cancelled_at = timezone.now()
        session.save(update_fields=["status", "cancelled_at"])

        return {
            "cancelled": True,
            "reason": "client_no_show",
            "session_id": str(session.id),
            "refund_issued": False,
        }

    @staticmethod
    def _cancel_trainer_no_show(session):
        """
        trainer didnt joined
        cancel session + refund to client.
        """
        logger.info(
            "NoShowService: trainer no-show for session %s. Cancelling with refund.",
            session.id,
        )
        session.status = "cancelled"
        session.cancelled_at = timezone.now()
        session.save(update_fields=["status", "cancelled_at"])

        try:
            refund_result = SessionRefundService.process_session_refund(
                session=session,
                reason="trainer_no_show",
            )
            logger.info(
                "NoShowService: refund issued for session %s → %s",
                session.id, refund_result,
            )
        except Exception:
            logger.exception(
                "NoShowService: refund FAILED for session %s after trainer no-show.",
                session.id,
            )
            raise 

        return {
            "cancelled": True,
            "reason": "trainer_no_show",
            "session_id": str(session.id),
            "refund_issued": True,
            "refund_result": refund_result,
        }