import logging
from django.utils import timezone
from django.db import DatabaseError

logger = logging.getLogger(__name__)

from ...models import TrainingSession
from ...choices import TrainingSessionStatus


class VideoSessionService:

    @staticmethod
    def mark_started(session: TrainingSession):
        try:
            if session.video_session_started_at:
                return

            session.video_session_started_at = timezone.now()
            session.status = TrainingSessionStatus.ONGOING

            session.save(update_fields=[
                "video_session_started_at",
                "status"
            ])

        except DatabaseError:
            logger.exception("Failed to mark session started", extra={"session_id": session.id})
            raise


    @staticmethod
    def mark_ended(session: TrainingSession):
        try:
            session.video_session_ended_at = timezone.now()
            session.status = TrainingSessionStatus.COMPLETED

            session.save(update_fields=[
                "video_session_ended_at",
                "status"
            ])

        except DatabaseError:
            logger.exception("Failed to mark session ended", extra={"session_id": session.id})
            raise


    @staticmethod
    def add_recording(session: TrainingSession, url: str):
        try:
            if not url:
                logger.warning("Recording URL missing", extra={"session_id": session.id})
                return

            session.recording_url = url
            session.save(update_fields=["recording_url"])

        except DatabaseError:
            logger.exception("Failed to add recording", extra={"session_id": session.id})
            raise