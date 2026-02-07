from rest_framework import serializers
from personal_training.models import TrainingSession


class TrainerSessionListSerializer(serializers.ModelSerializer):
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
            "status",
            "client_name",
        ]
