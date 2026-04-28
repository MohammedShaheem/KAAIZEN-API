from rest_framework import serializers
from personal_training.models import TrainingSession

class SessionRatingSerializer(serializers.Serializer):
    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        min_value=1,
        max_value=5
    )

    def validate(self, attrs):
        session = self.context.get("session")
        if session.client_rating is not None:
            raise serializers.ValidationError("You have already rated this session.")
        if session.status != "completed":
            raise serializers.ValidationError("Session is not completed yet.")
        return attrs