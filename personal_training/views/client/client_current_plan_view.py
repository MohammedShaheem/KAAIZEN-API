from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from clients.permissions import IsClient
from personal_training.services.client.client_current_plan_service import (
    ClientCurrentPlanService
)
from personal_training.serializers.client.client_current_plan import (
    ClientCurrentPlanSerializer
)


class ClientCurrentPlanView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        try:
            data = ClientCurrentPlanService.get_current_plan(
                user=request.user
            )

            serializer = ClientCurrentPlanSerializer(data)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except ValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND
            )
