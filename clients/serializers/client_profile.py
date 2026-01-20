from rest_framework import serializers
from clients.models import ClientProfile
from clients.services.calculations import (
    calculate_daily_calories,
    calculate_water_goal
)
from ..models import MealAllocation
import logging

logger = logging.getLogger(__name__)

class ClientProfileSerializer(serializers.ModelSerializer):
    logger.info("from client profile serializer")

    class Meta:
        model = ClientProfile
        exclude = ["user"]
        read_only_fields = (
            "target_daily_calories",
            "water_goal_ml",
            "created_at",
            "updated_at"
        )
    
    
    def create(self, validated_data):
        logger.info("from create of client profile serializer")

        user = self.context["request"].user
        
        validated_data["user"] = user
        validated_data["target_daily_calories"] =  calculate_daily_calories(validated_data)
        validated_data["water_goal_ml"] = calculate_water_goal(validated_data)

        profile = super().create(validated_data)
        
        # creating the time based targets for meal entry
        self._initialize_meal_allocations(profile)
        return profile

    
    
    # here instance is the already created profile
    def update(self,instance,validated_data):
        instance.target_daily_calories = calculate_daily_calories(instance)
        instance.water_goal_ml = calculate_water_goal(instance)
        self._initialize_meal_allocations(instance, update=True)
        return super().update(instance, validated_data) 
    
    
    
    
    
    def _initialize_meal_allocations(self, profile, update=False):
        defaults = {
            'breakfast': 25.0,
            'morning_snack': 12.5,
            'lunch': 25.0,
            'evening_snack': 12.5,
            'dinner': 25.0,
        }
        daily_cal = profile.target_daily_calories or 0
        
        for meal_type, pct in defaults.items():
            allocation, created = MealAllocation.objects.get_or_create(
                profile=profile,
                meal_type=meal_type,
                defaults={'percentage': pct}
            )
            #this computation is for when the user edit thier profile like editing the weight,activity level,etc..
            #their daily calory intake will be also changed so that this change want to be reflected in the alocation
            #computing raw cal
            allocation.target_calories = (daily_cal * pct) / 100
            if update and not created:
                if allocation.percentage > 0:
                    allocation.target_calories = (daily_cal * allocation.percentage) / 100
                else:
                    allocation.percentage = pct
                    allocation.target_calories = (daily_cal * pct) / 100
            allocation.save()