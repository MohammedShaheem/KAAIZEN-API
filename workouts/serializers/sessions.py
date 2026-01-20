from rest_framework import serializers
from uuid import UUID

class StartSessionSerializer(serializers.Serializer):
    category_id = serializers.UUIDField(required=False)


class HeartbeatSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    workout_id = serializers.UUIDField()
    effective_play_time_seconds = serializers.IntegerField(min_value=0)
    current_video_time_seconds = serializers.IntegerField(min_value=0)
    is_playing = serializers.BooleanField()


class CompleteSessionSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    notes = serializers.CharField(required=False, allow_blank=True)
