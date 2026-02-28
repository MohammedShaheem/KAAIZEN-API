from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from clients.permissions import IsClient
from personal_training.serializers.booking.trainer_selection_serializer import (
    TrainerSelectionSerializer
)
from personal_training.services.booking.trainer_selection_service import (
    TrainerSelectionService
)


class TrainerSelectionView(APIView):
    permission_classes = [IsClient]

    def post(self, request):
        serializer = TrainerSelectionSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            try:
                TrainerSelectionService.select_trainer_and_lock_slot(
                    client_id=request.user.id,
                    trainer_id=serializer.validated_data["trainer_id"]
                )
            except Exception as e:
                print("error form trainerselection",e)

            return Response(
                {"detail": "Trainer reserved successfully"},
                status=status.HTTP_200_OK
            )

        except ValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return Response(
                {"detail": "Unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
