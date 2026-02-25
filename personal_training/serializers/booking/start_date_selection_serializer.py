from rest_framework import serializers
from django.utils import timezone
from datetime import date


class StartDateSelectionSerializer(serializers.Serializer):
    start_date = serializers.DateField()

    def validate_start_date(self, value):
        today = timezone.localdate()

        if value < today:
            raise serializers.ValidationError("Start date cannot be in the past.")

        return value