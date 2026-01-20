from rest_framework import serializers
from ..models import MealAllocation
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
from .client_profile import ClientProfileSerializer

class MealAllocationSerializer(serializers.ModelSerializer):
    
    percentage = serializers.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    
    target_calories = serializers.FloatField(
        validators=[MinValueValidator(0.0)],
        
    )

    class Meta:
        model = MealAllocation
        fields = ['meal_type', 'percentage', 'target_calories']
        read_only_fields = ['profile']  

    
    def validate_target_calories(self, value):
        daily_cal = self.context['profile'].target_daily_calories or 0
        if value > daily_cal:
            raise serializers.ValidationError(
                f"Target calories ({value}) cannot exceed daily total ({daily_cal})."
            )
        return round(value, 2)
    

    def validate(self, data):
        profile = self.context['profile']
        # excluding the currently user added field value
        current_sum = profile.meal_allocations.exclude(id=self.instance.id if self.instance else None).aggregate(total=Sum('percentage'))['total'] or 0.0
        # the values that the user newly added
        new_pct = data.get('percentage', self.instance.percentage if self.instance else 0.0)
        if current_sum + new_pct > 100.0:
            raise serializers.ValidationError(
                f"Total percentages would exceed 100% (current: {current_sum}%, new: {new_pct}%). Adjust other meals."
            )
        return data

    # dynamically updating both fields
    def update(self, instance, validated_data):
        daily_cal = self.context['profile'].target_daily_calories or 0
        if 'percentage' in validated_data:
            pct = round(validated_data['percentage'], 2)
            validated_data['target_calories'] = round((daily_cal * pct) / 100, 2)
            instance.percentage = pct
        elif 'target_calories' in validated_data:
            cal = round(validated_data['target_calories'], 2)
            if daily_cal > 0:
                validated_data['percentage'] = round((cal / daily_cal) * 100, 2)
            instance.target_calories = cal

        super().update(instance, validated_data)
        return instance