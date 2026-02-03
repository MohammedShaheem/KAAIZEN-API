from django.db import models
from django.core.exceptions import ValidationError
from clients.models import ClientProfile
from trainers.models import TrainerProfile
from.choices import TrainingSessionStatus
# Create your models here.

class ClientPlan(models.Model):
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="training_plans"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    sessions_per_week = models.PositiveIntegerField(default=6)
    session_duration_minutes = models.PositiveIntegerField(default=60)
    session_duration = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["client", "is_active"]),
        ]
    def clean(self):
        super().clean()
        if self.start_date > self.end_date:
            raise ValidationError("Plan start date cannot be after end date.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
#####################################################################################


class ClientTrainerAssignment(models.Model):
    client = models.OneToOneField(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="trainer_assignment"
    )

    trainer = models.ForeignKey(
        TrainerProfile,
        on_delete=models.PROTECT,
        related_name="assigned_clients"
    )

    preferred_start_time = models.TimeField()
    preferred_end_time = models.TimeField()

    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["trainer", "is_active"]),
        ]

    def clean(self):
        super().clean()
        if self.preferred_start_time >= self.preferred_end_time:
            raise ValidationError(
                "Preferred start time must be before preferred end time."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

###################################################################################


class TrainingSession(models.Model):
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="training_sessions"
    )

    trainer = models.ForeignKey(
        TrainerProfile,
        on_delete=models.CASCADE,
        related_name="training_sessions"
    )

    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    status = models.CharField(
        max_length=30,
        choices=TrainingSessionStatus.choices,
        default=TrainingSessionStatus.SCHEDULED
    )

    created_by_system = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "training_sessions"
        indexes = [
            models.Index(fields=["trainer", "session_date"]),
            models.Index(fields=["client", "session_date"]),
            models.Index(fields=["trainer", "session_date", "start_time"]),
        ]

    def clean(self):
        super().clean()

        if self.start_time >= self.end_time:
            raise ValidationError("Session start time must be before end time.")

        overlapping = TrainingSession.objects.filter(
            trainer=self.trainer,
            session_date=self.session_date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(id=self.id)

        if overlapping.exists():
            raise ValidationError(
                "This session overlaps with another session for the trainer."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.client.email} → "
            f"{self.trainer.user.email} | "
            f"{self.session_date} "
            f"{self.start_time}-{self.end_time}"
        )

#######################################################################################

class MonthlyCancellationCounter(models.Model):
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="monthly_cancellations"
    )

    month = models.DateField()  
    cancellations_used = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("client", "month")
        indexes = [
            models.Index(fields=["client", "month"]),
        ]

################################################################################

class DeferredCredit(models.Model):
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="deferred_credits"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    source_session = models.ForeignKey(
        TrainingSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_redeemed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["client", "is_redeemed"]),
        ]
        
