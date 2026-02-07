from rest_framework import serializers
from datetime import time

from personal_training.constant.scheduling import SESSION_TYPES
from personal_training.models import ClientTrainerAssignment


class SessionPreferenceSerializer(serializers.Serializer):
    session_type = serializers.ChoiceField(
        choices=SESSION_TYPES.keys()
    )
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

    trainer_id = serializers.IntegerField()

    def validate(self, data):
        session_type = data["session_type"]
        start_time = data["start_time"]
        end_time = data["end_time"]

        window_start, window_end = SESSION_TYPES[session_type]

        if not (window_start <= start_time < window_end):
            raise serializers.ValidationError(
                "Start time is outside selected session type window."
            )

        if not (window_start < end_time <= window_end):
            raise serializers.ValidationError(
                "End time is outside selected session type window."
            )

        if start_time >= end_time:
            raise serializers.ValidationError(
                "Start time must be before end time."
            )

        return data


class ClientTrainerAssignmentSerializer(serializers.ModelSerializer):
    client_id = serializers.UUIDField(source="client.id", read_only=True)
    trainer_id = serializers.UUIDField(source="trainer.id", read_only=True)

    class Meta:
        model = ClientTrainerAssignment
        fields = [
            "id",
            "client_id",
            "trainer_id",
            "preferred_start_time",
            "preferred_end_time",
            "assigned_at",
            "is_active",
        ]
