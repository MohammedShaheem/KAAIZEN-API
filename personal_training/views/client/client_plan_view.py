from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
import logging

from clients.permissions import IsClient
from personal_training.serializers.client.client_plan import (
    ClientPlanCreateSerializer,
    ClientPlanSerializer
)
from personal_training.services.client.client_plan_service import ClientPlanService
from personal_training.models import ClientPlan

logger = logging.getLogger(__name__)

class ClientPlanView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        client = request.user.client_profile

        plans = ClientPlan.objects.filter(
            client=client
        ).order_by("-created_at")

        serializer = ClientPlanSerializer(plans, many=True)
        logger.info(f"response data from clientplanview{serializer.data}")
        
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        
        serializer = ClientPlanCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        try:
            serializer.is_valid(raise_exception=True)

            client = request.user.client_profile
            plan = serializer.validated_data["plan_id"]
            start_date = serializer.validated_data.get("start_date")

            plan = ClientPlanService.create_plan(
                client=client,
                plan_id=plan.id,
                start_date=start_date
            )

            return Response(
                ClientPlanSerializer(plan).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.exception("Client plan creation failed")
            return Response(
                {"detail": "Something went wrong while creating the plan."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except ValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return Response(
                {"detail": "Something went wrong while creating the plan."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
