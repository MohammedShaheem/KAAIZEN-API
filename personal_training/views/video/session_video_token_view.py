import logging
from django.shortcuts import get_object_or_404
from django.db import DatabaseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from personal_training.models import TrainingSession
from personal_training.services.video.zego_token_service import ZegoTokenService

logger = logging.getLogger(__name__)


class SessionVideoTokenAPIView(APIView):
    def get(self, request, session_id: int):
        try:

            session = get_object_or_404(TrainingSession, id=session_id)

            if not session.room_id:
                logger.warning(
                    "Session missing room_id",
                    extra={"session_id": session_id}
                )
                return Response(
                    {"detail": "Session is not configured for video."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = request.user
            
            is_client = hasattr(user, "clientprofile") and user.clientprofile == session.client
            is_trainer = hasattr(user, "trainerprofile") and user.trainerprofile == session.trainer

            if not (is_client or is_trainer):
                logger.warning(
                    "Unauthorized video token access attempt",
                    extra={
                        "user_id": user.id,
                        "session_id": session_id,
                    },
                )
                return Response(
                    {"detail": "You are not allowed to access this session."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            token_data = ZegoTokenService.generate(
                user_id=str(user.id),
                room_id=session.room_id,
            )

            return Response(token_data, status=status.HTTP_200_OK)

        except DatabaseError:
            logger.exception("Database error while fetching session")
            return Response(
                {"detail": "Server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception:
            logger.exception("Unexpected error in SessionVideoTokenAPIView")
            return Response(
                {"detail": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
