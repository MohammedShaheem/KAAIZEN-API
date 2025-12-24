from rest_framework import serializers
from users.models import User
from clients.models import ClientProfile


class AdminClientListSerilalizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "is_active",
            "created_at"
        )
        
class AdminClinetDetailSerialier(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    is_active = serializers.BooleanField(source="user.is_active")
    
    class Meta:
        model = ClientProfile
        fields = (
            "email",
            "is_active",
            "full_name",
            "date_of_birth",
            "gender",
            "height_cm",
            "weight_kg",
            "fitness_goal",
            "workout_experience",
            "preferred_workout_types",
            "goal_speed",
            "diet_preference",
            "daily_activity_level",
            "target_daily_calories",
            "water_goal_ml",
        )
        read_only_fields = fields
        
        
        
        
        
        
        
        
        
        
        
class AdminTrainerListSerilalizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "is_active",
            "is_verified",
            "created_at"
        )