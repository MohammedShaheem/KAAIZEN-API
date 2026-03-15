from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from notification.models import TrackingReminder
from notification.services.send_push_service import send_push
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_tracking_reminders():

    logger.info("Celery task started: send_tracking_reminders")

    now = timezone.localtime()
    logger.info(f"Current time: {now}")
    one_minute_ago = now - timedelta(minutes=1)


    reminders = TrackingReminder.objects.filter(
        reminder_time__range=(
            one_minute_ago.time(),
            now.time(),
        ),
        is_active=True
    )
    
    logger.info(f"Reminders found: {reminders.count()}")

    for reminder in reminders:
        logger.info(f"Processing reminder id={reminder.id}")

        if reminder.reminder_type == "water":
            title = "Hydration Reminder"
            body = "Drink water now"

        elif reminder.reminder_type == "food":
            title = "Meal Reminder"
            body = "Log your meal"

        else:
            title = "Sleep Reminder"
            body = "Prepare for sleep"

        logger.info(f"Sending push to user {reminder.user.id}")

        send_push(reminder.user, title, body)

    logger.info("Celery task completed")