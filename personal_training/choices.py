from django.db.models import TextChoices


class TrainingSessionStatus(TextChoices):
    REASSIGNED = 'reassigned','Reassigned'
    SCHEDULED = "scheduled", "Scheduled"
    COMPLETED = "completed", "Completed"
    CANCELED_EARLY = "canceled_early", "Canceled Early"
    CANCELED_LATE = "canceled_late", "Canceled Late"
    NO_SHOW = "no_show", "No Show"
    TRAINER_UNAVAILABLE = "trainer_unavailable", "Trainer Unavailable"


class PlanStatusChoice(TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    ACTIVE =  "active", "Active"
    CANCELLED = "cancelled", "Cancelled"
    EXPIRED =   "expired", "Expired"
    FAILED = "failed", "Payment Failed"
    
class PaymentStatusChoice(TextChoices):
    SUCCEEDED = "succeeded", "Succeeded"
    PENDING =  "pending", "Pending"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"