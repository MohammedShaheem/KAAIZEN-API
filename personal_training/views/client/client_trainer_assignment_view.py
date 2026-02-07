from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from clients.permissions import IsClient
from trainers.models import TrainerProfile
from personal_training.serializers.client.client_trainer_assignment import (
    SessionPreferenceSerializer,
    ClientTrainerAssignmentSerializer
)
from personal_training.services.client.client_trainer_assignment_service import (
    ClientTrainerAssignmentService
)


class ClientTrainerAssignmentView(APIView):
    permission_classes = [IsClient]
    def post(self, request):
        serializer = SessionPreferenceSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            client = request.user
            trainer_id = serializer.validated_data["trainer_id"]
            start_time = serializer.validated_data["start_time"]
            end_time = serializer.validated_data["end_time"]

            trainer = TrainerProfile.objects.get(id=trainer_id)

            assignment = ClientTrainerAssignmentService.assign_trainer_and_create_sessions(
                client=client,
                trainer=trainer,
                preferred_start_time=start_time,
                preferred_end_time=end_time
            )

            return Response(
                ClientTrainerAssignmentSerializer(assignment).data,
                status=status.HTTP_201_CREATED
            )

        except TrainerProfile.DoesNotExist:
            return Response(
                {"detail": "Selected trainer does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        except ValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return Response(
                {"detail": "Something went wrong while assigning trainer."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
