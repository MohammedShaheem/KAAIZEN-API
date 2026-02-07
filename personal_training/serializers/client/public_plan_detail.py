from rest_framework import serializers
from personal_training.models import TrainingPlan


class PublicTrainingPlanDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainingPlan
        fields = [
            "id",
            "name",
            "duration_days",
            "price",
            "description",
        ]
