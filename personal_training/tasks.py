from celery import shared_task
from personal_training.services.client.client_trainer_assignment_service import ClientTrainerAssignmentService
from personal_training.models import ClientTrainerAssignment
from personal_training.services.video.no_show_service import NoShowCancellationService
import logging
from celery.exceptions import MaxRetriesExceededError

logger = logging.getLogger(__name__)


@shared_task
def maintain_sessions():
    assignments = ClientTrainerAssignment.objects.filter(is_active=True)

    for assignment in assignments.iterator():
        ClientTrainerAssignmentService.ensure_upcoming_sessions(assignment)
        
        
@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def check_session_no_show(self, session_id):
    """
    fires 10 minutes after either party joins.
    auto-cancels the session if the other party never showed.
    """
    
    try:
        result = NoShowCancellationService.check_and_cancel_if_no_show(session_id)
        logger.info("NoShowTask session=%s result=%s", session_id, result)
        return result
 
    except Exception as exc:
        logger.exception(
            "NoShowTask failed for session=%s (attempt %s/%s)",
            session_id,
            self.request.retries + 1,
            self.max_retries + 1,
        )
        try:
           
            raise self.retry(exc=exc)
 
        except MaxRetriesExceededError:
            
            logger.critical(
                "NoShowTask EXHAUSTED all %s retries for session=%s. "
                "Manual intervention required — the session may be stuck in "
                "'scheduled' status and the client's refund may not have been "
                "issued. Last error: %s",
                self.max_retries,
                session_id,
                exc,
            )
            raise  