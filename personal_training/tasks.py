from celery import shared_task
from personal_training.services.client.client_trainer_assignment_service import ClientTrainerAssignmentService
from personal_training.models import ClientTrainerAssignment

@shared_task
def maintain_sessions():
    assignments = ClientTrainerAssignment.objects.filter(is_active=True)

    for assignment in assignments.iterator():
        ClientTrainerAssignmentService.ensure_upcoming_sessions(assignment)