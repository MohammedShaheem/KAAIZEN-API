from trainers.models import TrainerProfile
from rest_framework import serializers

class TrainerVerificationListSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    user_id = serializers.UUIDField(source="user.id")

    class Meta:
        model = TrainerProfile
        fields = [
            "id",
            "user_id",
            "email",
            "full_name",
            "skills",
            "experience_certificate",
            "created_at",
        ]
        
class TrainerVerificationDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    user_id = serializers.UUIDField(source="user.id")

    class Meta:
        model = TrainerProfile
        fields = [
            "id",
            "user_id",
            "email",
            "full_name",
            "gender",
            "bio",
            "skills",
            "experience_certificate",
            "is_verified",
            "created_at",
        ]