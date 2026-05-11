from django.db import models
from django.conf import settings
from core.models import UUIDModel,TimeStampedModel
from .choices import (
    Gender,
    FitnessGoal,
    WorkoutExperience,
    PreferredWorkoutType,
    GoalSpeed,
    DietPreference,
    DailyActivityLevel,
)
from nutrition.models import MealEntry

class ClientProfile(UUIDModel, TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile"
    )
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True,blank=True)
    
    gender = models.CharField(max_length=20,
                              choices=Gender.choices,
                              null=True,blank=True)
    
    height_cm = models.PositiveIntegerField(null=True,blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, 
                                    null=True,blank=True)
    
    fitness_goal = models.CharField(max_length=100,
                                    choices=FitnessGoal.choices,
                                    null=True,blank=True)
    
    workout_experience = models.CharField(max_length=100,
                                          choices=WorkoutExperience.choices,
                                          blank=True,null=True)
    
    preferred_workout_type = models.CharField(max_length=50,
                                              choices=PreferredWorkoutType.choices,
                                              null=True,blank=True)
    
    goal_speed = models.CharField(max_length=50,
                                  choices=GoalSpeed.choices,
                                  null=True,blank=True)
      
    diet_preference = models.CharField(max_length=50,
                                       choices=DietPreference.choices,
                                       null=True,blank=True)
    daily_activity_level = models.CharField(max_length=50,
                                            choices=DailyActivityLevel.choices,
                                            null=True,blank=True)
    
    profile_picture = models.URLField(
        max_length=500,
        blank=True,
        null=True
    )
    
    target_daily_calories = models.PositiveIntegerField(null=True,blank=True)
    water_goal_ml=models.PositiveIntegerField(null=True,blank=True)
    daily_calorie_burn_goal = models.PositiveIntegerField(null=True, blank=True) 
    
    class Meta:
        db_table = "client_profiles"
        indexes = [
            models.Index(fields=["user"])
        ]
    
    def __str__(self):
        return f"{self.user.email} - Client Profile"
    
# 6 times divided meal entries
class MealAllocation(models.Model):
    MEAL_TYPES = MealEntry.MEAL_TYPES  

    profile = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name='meal_allocations'
    )
    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPES,
        
    )
    percentage = models.FloatField(
        default=0.0,
        
    )
    target_calories = models.FloatField(
        default=0.0,
        
    )
    class Meta:
        unique_together = ['profile', 'meal_type']
        indexes = [models.Index(fields=['profile', 'meal_type'])]
        verbose_name_plural = "Meal Allocations"
    
    def __str__(self):
        return f"{self.profile.user.email}'s {self.get_meal_type_display()}: {self.target_calories} kcal ({self.percentage}%)"