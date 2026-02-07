import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsClient

from personal_training.serializers.client.public_training_plan import (
    PublicTrainingPlanSerializer
)
from personal_training.services.client.public_training_plan_service import (
    PublicTrainingPlanService
)

logger = logging.getLogger(__name__)


class PublicTrainingPlanListView(APIView):
    
    permission_classes = [IsClient]

    def get(self, request):
        plans = PublicTrainingPlanService.list_active_plans()
        serializer = PublicTrainingPlanSerializer(plans, many=True)

        logger.info(
            "Returned %s active training plans for client %s",
            len(serializer.data),
            request.user.id,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
