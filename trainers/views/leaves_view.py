from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from trainers.models import TrainerLeave
from trainers.serializers.leaves import TrainerLeaveSerializer
from trainers.permissions import IsTrainer
from trainers.services.trainer_leave_service import TrainerLeaveService


class TrainerLeaveView(APIView):
    permission_classes = [IsTrainer]

    
    def get(self, request):
        trainer = request.user.trainer_profile

        leaves = TrainerLeave.objects.filter(
            trainer=trainer
        ).order_by("-start_date")

        serializer = TrainerLeaveSerializer(leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def post(self, request):
        serializer = TrainerLeaveSerializer(
            data=request.data,
            context={"request": request}
        )

        try:
            serializer.is_valid(raise_exception=True)

            trainer = request.user.trainer_profile
            start_date = serializer.validated_data["start_date"]
            end_date = serializer.validated_data["end_date"]
            reason = serializer.validated_data.get("reason", "")

            leave = TrainerLeaveService.create_leave(
                trainer=trainer,
                start_date=start_date,
                end_date=end_date,
                reason=reason
            )

            return Response(
                TrainerLeaveSerializer(leave).data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as exc:
            return Response(
                {"detail": exc.message if hasattr(exc, "message") else str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return Response(
                {"detail": "Something went wrong while applying for leave."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
