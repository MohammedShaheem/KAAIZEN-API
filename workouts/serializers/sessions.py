from rest_framework import serializers
from uuid import UUID
from workouts.models import WorkoutCategory

class StartSessionSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()

    def validate_category_id(self, value):
        if not WorkoutCategory.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Invalid workout category."
            )
        return value



class HeartbeatSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    workout_id = serializers.UUIDField()
    effective_play_time_seconds = serializers.IntegerField(min_value=0)
    current_video_time_seconds = serializers.IntegerField(min_value=0)
    is_playing = serializers.BooleanField()
    
    def validate(self, data):
        if data["current_video_time_seconds"] < data["effective_play_time_seconds"]:
            raise serializers.ValidationError(
                "Current video time cannot be less than effective play time."
            )
        return data 


class CompleteSessionSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    notes = serializers.CharField(required=False, allow_blank=True)
