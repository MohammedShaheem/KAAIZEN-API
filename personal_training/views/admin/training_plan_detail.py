import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from core.permissions import IsAdmin

from personal_training.services.admin.training_plan_detail_service import (
    TrainingPlanDetailService
)
from personal_training.serializers.admin.training_detail_Serializer import TrainingPlanDetailSerializer

logger = logging.getLogger(__name__)


class TrainingPlanAdminDetailView(APIView):

    permission_classes = [IsAdmin]

    def get(self, request, plan_id):
        try:
            plan = TrainingPlanDetailService.get_plan_with_clients(plan_id)
            serializer = TrainingPlanDetailSerializer(plan)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, plan_id):
        try:
            is_active = request.data.get("is_active")

            if is_active in [True, False]:
                pass
            elif isinstance(is_active, str):
                if is_active.lower() == "true":
                    is_active = True
                elif is_active.lower() == "false":
                    is_active = False
                else:
                    raise ValidationError("Invalid value for is_active.")
            else:
                raise ValidationError("is_active must be a boolean.")

            plan = TrainingPlanDetailService.set_plan_active_status(
                plan_id=plan_id,
                is_active=is_active
            )

            serializer = TrainingPlanDetailSerializer(plan)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
