from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
import logging

from clients.permissions import IsClient
from personal_training.serializers.client.client_plan import (
    ClientPlanSerializer
)
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
