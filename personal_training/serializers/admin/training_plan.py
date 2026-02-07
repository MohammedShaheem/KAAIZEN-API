from rest_framework import serializers
 
from personal_training.models import TrainingPlan


class TrainingPlanSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = TrainingPlan
        read_only_fields = ["id","created_at"]
        fields = [
            "id",
            "name",
            "duration_days",
            "price",
            "description",
            "is_active",
            "created_at",
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
