from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from core.permissions import IsClient
from personal_training.serializers.booking.start_date_selection_serializer import StartDateSelectionSerializer
from personal_training.services.booking.start_date_selection_service import StartDateSelectionService


class StartDateSelectionView(APIView):
    permission_classes = [IsClient]

    def post(self, request):
        serializer = StartDateSelectionSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            StartDateSelectionService.select_start_date(
                client_id=request.user.id,
                start_date=serializer.validated_data["start_date"]
            )

            return Response(
                {"detail": "Start date selected successfully"},
                status=status.HTTP_200_OK
            )

        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )