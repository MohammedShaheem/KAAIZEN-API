from rest_framework import serializers
from ai_plan.models import WorkoutDietPlan


class WorkoutDietPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutDietPlan
        fields = ["plan_data", "created_at", "updated_at"]
