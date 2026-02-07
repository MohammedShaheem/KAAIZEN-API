from rest_framework import serializers

from personal_training.models import ClientPlan
from personal_training.models import TrainingPlan


class ClientPlanCreateSerializer(serializers.Serializer):
    plan_id = serializers.UUIDField()
    start_date = serializers.DateField(required=False)

    def validate_plan_id(self, value):
        try:
            plan = TrainingPlan.objects.get(id=value, is_active=True)
        except TrainingPlan.DoesNotExist:
            raise serializers.ValidationError("Selected plan is not available.")

        return plan   



class ClientPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPlan
        fields = [
            "id",
            "start_date",
            "end_date",
            "sessions_per_week",
            "session_duration_minutes",
            "is_active",
            "created_at"
        ]
        read_only_fields = fields
