from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsTrainer
from trainers.services.trainer_dashboard import (
    TrainerDashboardService
)
from trainers.serializers.dashboard import (
    TrainerDashboardSerializer
)


class TrainerDashboardView(APIView):
    permission_classes = [IsTrainer]

    def get(self, request):
        data = TrainerDashboardService.get_dashboard_summary(request.user)
        serializer = TrainerDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
