from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db.models import Q

from core.permissions import IsClient
from trainers.models import TrainerProfile
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
            
            trainers_exist = TrainerProfile.objects.filter(
                    is_active=True,
                    is_verified=True
                ).filter(
                    Q(shift_type=session_type) | Q(shift_type="both")
                ).exists()

            
            if not trainers_exist:
                return Response(
                    {
                        "message": "No trainers available for this session type. Please choose another.",
                        "no_trainers": True
                    },
                    status=status.HTTP_200_OK
                )

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
