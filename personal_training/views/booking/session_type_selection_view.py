from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from core.permissions import IsClient
from personal_training.serializers.booking.session_type_selection_serializer import (
    SessionTypeSelectionSerializer
)
from personal_training.services.booking.slot_service import SlotService


class SessionTypeSelectionView(APIView):
    permission_classes = [IsClient]

    def post(self, request):
        serializer = SessionTypeSelectionSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            session_type = serializer.validated_data["session_type"]

            slots = SlotService.generate_and_store_slots(
                client_id=request.user.id,
                session_type=session_type
            )

            return Response(
                {"slots": slots},
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
