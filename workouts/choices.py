from django.db import models

class WorkoutDifficulty(models.TextChoices):
    BEGINNER = "beginner", "Beginner"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"
    
    
class StatusChoices(models.TextChoices):
    ACTIVE = "active","Active"
    COMPLETED = "completed","Completed"
    ABANDONED = "abandoned","Abandoned"