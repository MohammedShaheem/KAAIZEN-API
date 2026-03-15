from rest_framework import serializers
from notification.models import TrackingReminder

class TrackingReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingReminder
        fields = ["id", "reminder_type", "reminder_time", "is_active"]