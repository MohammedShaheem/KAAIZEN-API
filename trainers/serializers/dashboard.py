from rest_framework import serializers
from personal_training.models import TrainingSession


class UpcomingSessionSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source="client.full_name",
        read_only=True
    )

    class Meta:
        model = TrainingSession
        fields = [
            "id",
            "session_date",
            "start_time",
            "end_time",
            "client_name",
        ]


class TrainerDashboardSerializer(serializers.Serializer):
    stats = serializers.DictField()
    upcoming_sessions = UpcomingSessionSerializer(many=True)
    trainer = serializers.DictField()
