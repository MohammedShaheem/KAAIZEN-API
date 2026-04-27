from rest_framework import serializers
from workouts.models import WorkoutSession, SessionVideo

class RecentSessionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', default='Unknown')
    category_image = serializers.URLField(source='category.category_image_url', default=None)
    video_count = serializers.SerializerMethodField()

    class Meta:
        model = WorkoutSession
        fields = [
            'id', 'category_name', 'category_image',
            'total_calories_burned', 'total_duration_seconds',
            'status', 'started_at', 'completed_at', 'video_count'
        ]

    def get_video_count(self, obj):
        return obj.session_videos.count()