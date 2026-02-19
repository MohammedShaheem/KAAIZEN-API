from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from trainers.models import TrainerLeave
from trainers.serializers.leaves import TrainerLeaveSerializer
from core.permissions import IsTrainer


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
        serializer.is_valid(raise_exception=True)
        leave = serializer.save()

        return Response(
            TrainerLeaveSerializer(leave).data,
            status=status.HTTP_201_CREATED
        )
