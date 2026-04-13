import logging
from datetime import datetime, timedelta, date
from django.db import transaction, DatabaseError, IntegrityError
from django.core.exceptions import ValidationError
from django.utils.timezone import now, make_aware

from personal_training.models import (
    TrainingSession,
    MonthlyCancellationCounter
)
from personal_training.constant.cancellation import (
    MAX_CANCELLATIONS_PER_MONTH,
    REFUND_CUTOFF_HOURS
)

logger = logging.getLogger(__name__)


class SessionCancellationService:
   
    @staticmethod
    def _get_month_start(target_date: date):
        return target_date.replace(day=1)

    @staticmethod
    def _get_or_create_counter(client, session_date):
        month_start = SessionCancellationService._get_month_start(
            session_date
        )

        counter, _ = MonthlyCancellationCounter.objects.get_or_create(
            client=client,
            month=month_start,
            defaults={"cancellations_used": 0}
        )

        return counter

    @staticmethod
    def _session_datetime(session):
        """
        Combine date + time into a single datetime object and make it timezone aware
        """
        naive_dt = datetime.combine(
            session.session_date,
            session.start_time
        )

        return make_aware(naive_dt)


    @staticmethod
    @transaction.atomic
    def cancel_session(client, session_id):
        try:
            session = TrainingSession.objects.select_for_update().get(
                id=session_id,
                client=client,
                status="scheduled"
            )

            counter = SessionCancellationService._get_or_create_counter(
                client,
                session.session_date
            )

            if counter.cancellations_used >= MAX_CANCELLATIONS_PER_MONTH:
                refund_eligible = False
            else:
                session_dt = SessionCancellationService._session_datetime(
                    session
                )
                hours_before = (session_dt - now()).total_seconds() / 3600
                refund_eligible = hours_before >= REFUND_CUTOFF_HOURS

            session.status = (
                "canceled_early"
                if refund_eligible
                else "canceled_late"
            )
            session.save()

            if counter.cancellations_used < MAX_CANCELLATIONS_PER_MONTH:
                counter.cancellations_used += 1
                counter.save()

            return {
                "session": session,
                "refund_eligible": refund_eligible,
                "cancellations_used": counter.cancellations_used,
                "remaining_cancellations": max(
                    0,
                    MAX_CANCELLATIONS_PER_MONTH
                    - counter.cancellations_used
                )
            }

        except TrainingSession.DoesNotExist:
            raise ValidationError("Session not found or cannot be canceled.")

        except IntegrityError as e:
            logger.exception("Integrity error while canceling session")
            raise ValidationError(
                "Cancellation failed due to a data conflict."
            ) from e

        except DatabaseError as e:
            logger.exception("Database error while canceling session")
            raise ValidationError(
                "Server error while canceling session."
            ) from e

        except Exception as e:
            logger.exception("Unexpected error while canceling session")
            raise ValidationError(
                "Unexpected error occurred during cancellation."
            ) from e
