import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from core.permissions import IsClient

from personal_training.serializers.client.public_plan_detail import (
    PublicTrainingPlanDetailSerializer
)
from personal_training.services.client.public_plan_detail_servie import (
    PublicTrainingPlanDetailService
)

logger = logging.getLogger(__name__)


class PublicTrainingPlanDetailView(APIView):
   
    permission_classes = [IsClient]

    def get(self, request, plan_id):
        try:
            plan = PublicTrainingPlanDetailService.get_active_plan(plan_id)
            serializer = PublicTrainingPlanDetailSerializer(plan)

            logger.info(
                "Returned training plan detail | plan_id=%s | client=%s",
                plan_id,
                request.user.id
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
