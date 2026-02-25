from rest_framework import serializers
from personal_training.models import TrainingPlan


class CreateCheckoutSerializer(serializers.Serializer):
    plan_id = serializers.UUIDField()

    def validate_plan_id(self, value):
        try:
            plan = TrainingPlan.objects.get(id=value, is_active=True)
            return plan
        except TrainingPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive plan.")