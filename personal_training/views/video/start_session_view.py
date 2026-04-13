import logging

from django.shortcuts import get_object_or_404
from django.db import DatabaseError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ...models import TrainingSession
from ...services.video.session_service import VideoSessionService

logger = logging.getLogger(__name__)


class StartSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        try:
            session = get_object_or_404(TrainingSession, id=session_id)

            VideoSessionService.mark_started(session)

            return Response(
                {"message": "session started"},
                status=status.HTTP_200_OK
            )

        except DatabaseError:
            logger.exception("Failed to start session")
            return Response(
                {"detail": "failed to start session"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )