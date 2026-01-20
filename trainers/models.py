from django.db import models
from django.db import models
from django.conf import settings
from core.models import UUIDModel, TimeStampedModel
from .choices import Gender, Skill

# Create your models here.

class TrainerProfile(UUIDModel, TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trainer_profile'
    )
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    experience_certificate = models.URLField(max_length=500, blank=True, null=True)  
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        null=True,
        blank=True
    )
    bio = models.TextField(blank=True)
    skills = models.JSONField(default=list, blank=True) 
    
    is_verified = models.BooleanField(default=False, null=True,blank=True)
    verified_at = models.DateTimeField(null=True, blank=True) 
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="verified_trainers",
    )

    class Meta:
        db_table = 'trainer_profiles'
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.email} - Trainer Profile"