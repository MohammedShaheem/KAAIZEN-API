import logging
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db import DatabaseError, transaction
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from personal_training.models import TrainingSession
from personal_training.services.video.zego_token_service import ZegoTokenService
from personal_training.tasks import check_session_no_show
from trainers.models import TrainerProfile
from clients.models import ClientProfile

logger = logging.getLogger(__name__)
NO_SHOW_DELAY_SECONDS = 60


class SessionVideoTokenAPIView(APIView):
    """
        1. authorize access to correct client and trainer for the session
        2. tracks not joining time
        3. generate video token
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, session_id: int):
        try:
            session = get_object_or_404(TrainingSession, id=session_id)

            if not session.room_id:
                return Response(
                    {"detail": "Session is not configured for video."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = request.user
            trainer_profile = TrainerProfile.objects.filter(user_id=user.id).first()
            client_profile  = ClientProfile.objects.filter(user_id=user.id).first()

            is_trainer = trainer_profile == session.trainer
            is_client  = client_profile  == session.client

            if not (is_client or is_trainer):
                return Response(
                    {"detail": "You are not allowed to access this session."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            party = "trainer" if is_trainer else "client"

            with transaction.atomic():
                locked_session = (
                    TrainingSession.objects
                    .select_for_update()
                    .get(id=session_id)
                )

                now = timezone.now()
                update_fields = []

                if is_trainer and not locked_session.trainer_joined_at:
                    locked_session.trainer_joined_at = now
                    update_fields.append("trainer_joined_at")

                if is_client and not locked_session.client_joined_at:
                    locked_session.client_joined_at = now
                    update_fields.append("client_joined_at")

                if update_fields:
                    locked_session.save(update_fields=update_fields)

                    both_joined = (
                        locked_session.trainer_joined_at
                        and locked_session.client_joined_at
                    )
                    if not both_joined:
                        transaction.on_commit(
                            lambda: check_session_no_show.apply_async(
                                args=[session_id],
                                countdown=NO_SHOW_DELAY_SECONDS,
                            )
                        )
                        logger.info(
                            "NoShow task scheduled for session=%s by %s",
                            session_id, party,
                        )

            username = (
                client_profile.full_name if is_client
                else trainer_profile.full_name
            )

            token_data = ZegoTokenService.generate(
                user_id=str(user.id),
                room_id=session.room_id,
                expiry_seconds=3600,
                username=username,
            )

            return Response({
                "app_id":     token_data["appID"],
                "token":      token_data["token"],
                "user_id":    token_data["userID"],
                "room_id":    token_data["roomID"],
                "expires_at": token_data["expiresAt"],
                "user_name":  username,
            }, status=status.HTTP_200_OK)

        except Http404:
            raise

        except DatabaseError:
            logger.exception("Database error in SessionVideoTokenAPIView")
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