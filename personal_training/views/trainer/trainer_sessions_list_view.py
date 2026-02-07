from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from trainers.permissions import IsTrainer
from personal_training.services.trainer.trainer_session_service import (
    TrainerSessionService
)
from personal_training.serializers.trainer.session_list import (
    TrainerSessionListSerializer
)


class TrainerSessionListView(APIView):
    permission_classes = [IsTrainer]

    def get(self, request):
        try:
            data = TrainerSessionService.get_trainer_sessions(request.user)

            return Response(
                {
                    "recent_sessions": TrainerSessionListSerializer(
                        data["recent_sessions"], many=True
                    ).data,
                    "all_sessions": TrainerSessionListSerializer(
                        data["all_sessions"], many=True
                    ).data,
                },
                status=status.HTTP_200_OK
            )

        except ValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
