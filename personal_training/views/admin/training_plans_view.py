import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.exceptions import ValidationError
from core.permissions import IsAdmin

from personal_training.services.admin.training_plan_service import TrainingPlanService
from personal_training.serializers.admin.training_plan import TrainingPlanSerializer

logger = logging.getLogger(__name__)


class TrainingPlanAdminView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        plans = TrainingPlanService.list_plans_with_usage()
        logger.info(f"{plans}")
        serializer = TrainingPlanSerializer(plans, many=True)
        logger.info(f"response data from clientplanview{serializer.data}")

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TrainingPlanSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            plan = TrainingPlanService.create_plan(
                name=serializer.validated_data["name"],
                duration_days=serializer.validated_data["duration_days"],
                price=serializer.validated_data["price"],
                description=serializer.validated_data.get("description", ""),
                is_active=serializer.validated_data.get("is_active", True),
            )

            response_serializer = TrainingPlanSerializer(plan)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            logger.warning("Plan creation failed: %s", str(e))
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
