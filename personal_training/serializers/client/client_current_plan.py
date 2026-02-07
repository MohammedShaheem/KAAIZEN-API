from rest_framework import serializers
from personal_training.models import (
    ClientTrainerAssignment,
    TrainingSession
)
from trainers.models import TrainerProfile
from personal_training.models import TrainingPlan


class TrainerSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerProfile
        fields = [
            "id",
            "full_name",
            "gender",
            "bio",
            "rating",
            "experience_years",
            "is_verified",
        ]


class TrainingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSession
        fields = [
            "id",
            "session_date",
            "start_time",
            "end_time",
            "status",
        ]


class ClientTrainerAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientTrainerAssignment
        fields = [
            "preferred_start_time",
            "preferred_end_time",
            "assigned_at",
            "is_active",
        ]


class TrainingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingPlan
        fields = [
            "id",
            "name",
            "description",
            "duration_days",
            "price",
        ]

class ClientCurrentPlanSerializer(serializers.Serializer):
    plan = TrainingPlanSerializer()
    trainer = TrainerSummarySerializer()
    assignment = ClientTrainerAssignmentSerializer()
    sessions = TrainingSessionSerializer(many=True, required=False)

