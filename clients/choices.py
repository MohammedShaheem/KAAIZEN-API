from django.db import models

class Gender(models.TextChoices):
    MALE = "male",'Male'
    FEMALE = "female",'Female'
    OTHER = "other","Other"
    PREFER_NOT_TO_SAY = "na","Prefer not to say"
    
class FitnessGoal(models.TextChoices):
    WEIGHT_LOSS = "weight_loss","Weight Loss"
    MUSCLE_GAIN = "muscle_gain","Muscle Gain"
    MAINTENANCE = "maintenance","Maintenance"
    FLEXIBILITY = "flexibility","Flexibility"
    ENDURANCE = "endurance","Endurance"
    
class WorkoutExperience(models.TextChoices):
    BEGINER = "beginner","Beginner"
    INTERMEDIATE = "intermediate","Intermediate"
    ADVANCED = "advanced","Advanced"
    
class PreferredWorkoutType(models.TextChoices):
    STRENGHT = "strength_training","Strength Training"
    CARDIO = "cardio","Cardio"
    YOGA = "yoga","Yoga"
    HIIT = "hiit","HIIT"
    CROSSFIT = "crossfit","Crossfit"
    MIXED = "mixed","Mixed"
    
class GoalSpeed(models.TextChoices):
    SLOW = "slow","Slow"
    MODERATE = "moderate","Moderate"
    STEADY = "steady","Steady"
    FAST = "fast","Fast"
    
class DietPreference(models.TextChoices):
    VEG = "veg","Vegetarian"
    NON_VEG = "non_veg","Non_vegetarian"

class DailyActivityLevel(models.TextChoices):
    SEDENTARY = "sedentary","Sedentary"
    LIGHT = "light","Light Active"
    MODERATE = "moderate","Moderately Active"
    VERY_ACTIVE = "very_active","Very active"

