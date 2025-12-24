from rest_framework import serializers
from clients.models import ClientProfile
from clients.services.calculations import (
    calculate_daily_calories,
    calculate_water_goal
)

class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        exclude = ("user")
        read_only_fields = (
            "target_daily_calories",
            "water_goal_ml",
            "created_at",
            "updated_at"
        )
        
    def create(self,validated_data):
        user = self.context["request"].user
        
        profile = ClientProfile.objects.create(
            user=user,
            **validated_data
        )
        
        profile.target_daily_calories = calculate_daily_calories(profile)
        profile.water_goal_ml = calculate_water_goal(profile)
        profile.save()
        
        return profile
    
    def update(self,instance,validated_data):
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
            
        instance.target_daily_calories = calculate_daily_calories(instance)
        instance.water_goal_ml = calculate_water_goal(instance)
        
        instance.save()
        return instance