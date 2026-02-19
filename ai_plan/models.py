from django.db import models
from core.models import TimeStampedModel
from clients.models import ClientProfile
# Create your models here.

class WorkoutDietPlan(TimeStampedModel):
    client = models.OneToOneField(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name='ai_plan'
    )
    
    plan_data = models.JSONField()
    
    def __str__(self):
        return f"AI Plan - {self.client.full_name}"



