from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
import traceback

from clients.permissions import IsClient
from personal_training.serializers.booking.confirm_assignment_serializer import (
    ConfirmAssignmentSerializer
)
from personal_training.serializers.client.client_trainer_assignment import (
    ClientTrainerAssignmentSerializer
)
from personal_training.services.booking.confirm_assignment_service import (
    ConfirmAssignmentService
)


class ConfirmAssignmentView(APIView):
    
    permission_classes = [IsClient]

    def post(self, request):
        serializer = ConfirmAssignmentSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            try:
                assignment = ConfirmAssignmentService.confirm(
                    client=request.user
                )
            except Exception as e:
                print("error from confirm assignment",e)
                traceback.print_exc()
                raise

            return Response(
                ClientTrainerAssignmentSerializer(assignment).data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            print("Error in confirm service",e)
            traceback.print_exc()
            return Response(
                {"detail": "Unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
