from django.db import models
from users.models import User
# Create your models here.
class UserDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fcm_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    
    
class TrackingReminder(models.Model):
    REMINDER_TYPES = (
        ("food", "Food"),
        ("water", "Water"),
        ("sleep", "Sleep"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES)
    reminder_time = models.TimeField()
    is_active = models.BooleanField(default=True)