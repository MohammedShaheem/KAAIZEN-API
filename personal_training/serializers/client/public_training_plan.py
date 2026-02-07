from rest_framework import serializers
from personal_training.models import TrainingPlan


class PublicTrainingPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainingPlan
        fields = [
            "id",
            "name",
            "duration_days",
            "price",
            "description",
        ]
