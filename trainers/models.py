from django.db import models
from django.db import models
from django.conf import settings
from core.models import UUIDModel, TimeStampedModel
from .choices import Gender,Skill,ShiftType
from django.core.exceptions import ValidationError



# Create your models here.

class TrainerProfile(UUIDModel, TimeStampedModel):
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trainer_profile'
    )

    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)

    experience_years = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    experience_certificate = models.URLField(
        max_length=500,
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        null=True,
        blank=True
    )

    bio = models.TextField(blank=True)

    skills = models.JSONField(default=list, blank=True)

    shift_type = models.CharField(
        max_length=10,
        choices=ShiftType.choices,
        default=ShiftType.BOTH,
        null=True,
        blank=True
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
    )

    max_sessions_per_day = models.PositiveSmallIntegerField(
        default=5
    )

    is_active = models.BooleanField(
        default=True
    )

    is_verified = models.BooleanField(
        default=False,
        null=True,
        blank=True
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="verified_trainers"
    )

    class Meta:
        db_table = 'trainer_profiles'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.user.email} - Trainer Profile"


class TrainerAvailability(UUIDModel, TimeStampedModel):
    trainer = models.ForeignKey(
        TrainerProfile,
        on_delete=models.CASCADE,
        related_name="availabilities"
    )
    
    start_time = models.TimeField()

    end_time = models.TimeField()

    class Meta:
        db_table = "trainer_availabilities"
        indexes = [
            models.Index(fields=["trainer"]),
        ]
        unique_together = (
            "trainer",
            "start_time",
            "end_time",
        )

    def __str__(self):
        return (
            f"{self.trainer.user.email} | "
            f"{self.start_time} - {self.end_time}"
        )
        
class TrainerLeave(UUIDModel, TimeStampedModel):
    trainer = models.ForeignKey(
        TrainerProfile,
        on_delete=models.CASCADE,
        related_name="leaves"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    reason = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "trainer_leaves"
        indexes = [
            models.Index(fields=["trainer", "start_date", "end_date"]),
        ]
    
    def clean(self):
        super().clean()
        overlapping = TrainerAvailability.objects.filter(
            trainer=self.trainer,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(id=self.id)

        if overlapping.exists():
            raise ValidationError(
                "This availability overlaps with an existing time slot."
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.trainer.user.email} | "
            f"Leave {self.start_date} → {self.end_date}"
        )
