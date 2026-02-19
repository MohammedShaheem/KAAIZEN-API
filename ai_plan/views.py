from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from clients.models import ClientProfile
from ai_plan.models import WorkoutDietPlan
from ai_plan.serializer.plan_serializer import WorkoutDietPlanSerializer
from ai_plan.services.ai_plan_service import AIPlanService


class GenerateAIPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            client_profile = request.user.client_profile
        except ClientProfile.DoesNotExist:
            return Response(
                {"error": "Client profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            plan = client_profile.ai_plan  
        except WorkoutDietPlan.DoesNotExist:
            return Response(
                {"error": "AI plan not generated yet"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WorkoutDietPlanSerializer(plan)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        try:
            client_profile = request.user.client_profile
        except ClientProfile.DoesNotExist:
            return Response(
                {"error": "Client profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            plan = AIPlanService.create_or_update_plan(client_profile)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = WorkoutDietPlanSerializer(plan)
        return Response(serializer.data, status=status.HTTP_200_OK)

