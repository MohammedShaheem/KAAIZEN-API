import logging
from django.shortcuts import get_object_or_404
from django.db import DatabaseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from personal_training.models import TrainingSession
from personal_training.services.video.zego_token_service import ZegoTokenService
from django.conf import settings
from trainers.models import TrainerProfile
from clients.models import ClientProfile


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
            
            logger.warning(
                f"""
                user={user.id}
                user_client={getattr(user, 'clientprofile', None)}
                session_client={session.client}
                user_trainer={getattr(user, 'trainerprofile', None)}
                session_trainer={session.trainer}
                """
            )
            
            
            trainer_profile = TrainerProfile.objects.filter(
                    user_id=user.id
                ).first()
            client_profile = ClientProfile.objects.filter(
                user_id = user.id
            ).first()
            
            
            logger.debug("client profile form session video token",client_profile)
            logger.debug("trainer profile form session video token",trainer_profile)
            
            
            is_trainer = trainer_profile == session.trainer
            is_client = client_profile == session.client
            # is_client = hasattr(user, "clientprofile") and user.clientprofile == session.client
            # is_trainer = hasattr(user, "trainerprofile") and user.trainerprofile == session.trainer

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
                
            if client_profile:
                username = client_profile.full_name
            elif trainer_profile:
                username = trainer_profile.full_name
            else:
                raise 

            token_data = ZegoTokenService.generate(
                user_id=str(user.id),
                room_id=session.room_id,
                expiry_seconds=3600,
            )

            response_data = {
                "app_id": token_data["appID"],
                "token": token_data["token"],
                "user_id": token_data["userID"],
                "room_id": token_data["roomID"],
                "expires_at": token_data["expiresAt"],
                "user_name": username,
            }

            return Response(response_data, status=status.HTTP_200_OK)

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
