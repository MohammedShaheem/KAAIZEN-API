from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
import logging

from clients.permissions import IsClient
from trainers.serializers.trainer_profile import TrainerProfileSerializer
from personal_training.serializers.booking.slot_selecting import SlotSelectionSerializer
from personal_training.services.booking.slot_selection_service import SlotSelectionService

logger = logging.getLogger(__name__)



class SlotSelectionView(APIView):
    permission_classes = [IsClient]

    def post(self, request):
        serializer = SlotSelectionSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            start_time = serializer.validated_data["start_time"]
            end_time = serializer.validated_data["end_time"]

            trainers = SlotSelectionService.select_slot_and_fetch_trainers(
                client_id=request.user.id,
                start_time=start_time,
                end_time=end_time
            )

            trainer_data = TrainerProfileSerializer(trainers, many=True).data
            logger.info(f"trainer_data from slot selectionf{trainer_data}")
            

            return Response(
                {"available_trainers": trainer_data},
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
