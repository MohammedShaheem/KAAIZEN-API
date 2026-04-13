import logging

from django.shortcuts import get_object_or_404
from django.db import DatabaseError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ...models import TrainingSession
from ...services.video.session_service import VideoSessionService
from wallet.services.admin.admin_wallet_settlement_service import SessionPayoutService

logger = logging.getLogger(__name__)


class EndSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        try:
            session = get_object_or_404(TrainingSession, id=session_id)

            VideoSessionService.mark_ended(session)
            settlement_result = SessionPayoutService.settle_session(session.id)

            return Response(
                {
                    "message": "session ended",
                    "wallet_settlement": settlement_result
                },
                status=status.HTTP_200_OK
            )

        except DatabaseError:
            logger.exception("Failed to end session")
            return Response(
                {"detail": "failed to end session"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )