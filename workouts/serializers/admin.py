from rest_framework import serializers
from workouts.models import Workout, WorkoutCategory, MuscleGroup


class AdminWorkoutCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutCategory
        fields = ["id", "name"]
        read_only_fields = ["id"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                "Category name must be at least 3 characters long."
            )
        if WorkoutCategory.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return value

class AdminWorkoutSerializer(serializers.ModelSerializer):
    muscle_groups = serializers.PrimaryKeyRelatedField(
        queryset=MuscleGroup.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Workout
        fields = [
            "id",
            "title",
            "description",
            "category",
            "difficulty",
            "duration_seconds",
            "video_url",
            "video_public_id",
            "thumbnail_time",
            "equipment_needed",
            "muscle_groups",
            "met_value",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        
        def validate_video_url(self, value):
            if "res.cloudinary.com" not in value:
                raise serializers.ValidationError(
                    "Video URL must be a Cloudinary URL."
            )
            return value

    def validate_duration_seconds(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Duration must be a positive number of seconds."
            )
        return value