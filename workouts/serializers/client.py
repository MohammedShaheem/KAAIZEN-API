from rest_framework import serializers
from workouts.models import WorkoutCategory,Workout

class ClientWorkoutCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutCategory
        fields = '__all__'


class ClientWorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = [
            "id",
            "title",
            "description",
            "difficulty",
            "duration_seconds",
            "video_url",        
            "thumbnail_time",
            "equipment_needed",
            "met_value",
        ]
    
    def get_thumbnail_url(self, obj):
        return obj.get_thumbnail_url()