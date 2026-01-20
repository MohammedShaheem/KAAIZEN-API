from django.db.models import TextChoices

class Gender(TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'
    OTHER = 'other', 'Other'
    PREFER_NOT_TO_SAY = 'prefer_not_to_say', 'Prefer not to say'

class Skill(TextChoices):
    NUTRITION = 'nutrition', 'Nutrition'
    POSTURE_ALIGNMENT = 'posture_alignment', 'Posture Alignment'
    MINDFULNESS_FOCUS = 'mindfulness_focus', 'Mindfulness & Focus'
    MUSCLE_BUILDING = 'muscle_building', 'Muscle Building'
    STRENGTH_TRAINING = 'strength_training', 'Strength Training'
    WEIGHT_LOSS = 'weight_loss', 'Weight Loss'
    STRESS_MANAGEMENT = 'stress_management', 'Stress Management'
    FLEXIBILITY = 'flexibility', 'Flexibility'
    CORE_STRENGTHENING = 'core_strengthening', 'Core Strengthening'