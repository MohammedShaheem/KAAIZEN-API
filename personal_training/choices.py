from django.db.models import TextChoices


class TrainingSessionStatus(TextChoices):
    REASSIGNED = 'reassigned','Reassigned'
    SCHEDULED = "scheduled", "Scheduled"
    COMPLETED = "completed", "Completed"
    CANCELED_EARLY = "canceled_early", "Canceled Early"
    CANCELED_LATE = "canceled_late", "Canceled Late"
    NO_SHOW = "no_show", "No Show"
    TRAINER_UNAVAILABLE = "trainer_unavailable", "Trainer Unavailable"
