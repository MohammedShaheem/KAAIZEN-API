from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from trainers.permissions import IsTrainer
from personal_training.services.trainer.trainer_session_service import (
    TrainerSessionService
)
from personal_training.serializers.trainer.session_detail import (
    TrainerSessionDetailSerializer
)


class TrainerSessionDetailView(APIView):
    permission_classes = [IsTrainer]

    def get(self, request, session_id):
        try:
            session = TrainerSessionService.get_session_detail(
                request.user, session_id
            )

            serializer = TrainerSessionDetailSerializer(session)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND
            )
